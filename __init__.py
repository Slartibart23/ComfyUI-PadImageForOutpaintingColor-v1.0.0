import torch

__version__ = "1.0.0"


def _parse_hex_color(value: str):
    """Parse '#RRGGBB', 'RRGGBB', '#RGB' or 'RGB' into (r, g, b) floats 0..1.
    Falls back to neutral gray (like the original node) on invalid input."""
    s = (value or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return (0.5, 0.5, 0.5)
    try:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
    except ValueError:
        return (0.5, 0.5, 0.5)
    return (r, g, b)


class PadImageForOutpaintingColor:
    """Like the built-in 'Pad Image For Outpainting', but fills the padded
    area with a user-defined color (color picker + hex code in the UI)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "left": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 8}),
                "top": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 8}),
                "right": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 8}),
                "bottom": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 8}),
                "feathering": ("INT", {"default": 40, "min": 0, "max": 16384, "step": 1}),
                "color": ("STRING", {"default": "#808080"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "expand_image"
    CATEGORY = "image"

    def expand_image(self, image, left, top, right, bottom, feathering, color):
        b, h, w, c = image.shape
        r, g, bl = _parse_hex_color(color)

        new_h, new_w = h + top + bottom, w + left + right

        fill = torch.tensor([r, g, bl], dtype=image.dtype, device=image.device)
        if c == 4:  # keep alpha fully opaque in the padded area
            fill = torch.cat([fill, torch.ones(1, dtype=image.dtype, device=image.device)])
        elif c != 3:  # unusual channel count: replicate gray-ish average
            fill = torch.full((c,), (r + g + bl) / 3.0, dtype=image.dtype, device=image.device)

        new_image = fill.view(1, 1, 1, c).expand(b, new_h, new_w, c).clone()
        new_image[:, top:top + h, left:left + w, :] = image

        # --- mask (same behaviour as the built-in node, but vectorised) ---
        mask = torch.ones((new_h, new_w), dtype=torch.float32, device=image.device)
        t = torch.zeros((h, w), dtype=torch.float32, device=image.device)

        if feathering > 0 and feathering * 2 < h and feathering * 2 < w:
            big = torch.tensor(max(h, w), dtype=torch.float32, device=image.device)
            ys = torch.arange(h, dtype=torch.float32, device=image.device)
            xs = torch.arange(w, dtype=torch.float32, device=image.device)

            dt = ys if top != 0 else torch.full_like(ys, big)
            db = (h - ys) if bottom != 0 else torch.full_like(ys, big)
            dl = xs if left != 0 else torch.full_like(xs, big)
            dr = (w - xs) if right != 0 else torch.full_like(xs, big)

            dy = torch.minimum(dt, db).view(h, 1)
            dx = torch.minimum(dl, dr).view(1, w)
            d = torch.minimum(dy, dx)

            v = torch.clamp((feathering - d) / feathering, min=0.0)
            t = v * v

        mask[top:top + h, left:left + w] = t
        return (new_image, mask.unsqueeze(0))


NODE_CLASS_MAPPINGS = {
    "PadImageForOutpaintingColor": PadImageForOutpaintingColor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PadImageForOutpaintingColor": "Pad Image For Outpainting (Color)",
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
