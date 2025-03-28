import os
import random
from PIL import Image
from tqdm import tqdm

# Set a random seed for reproducibility
random.seed(42)

def get_pixel(image, x, y):
    """Get the pixel value at (x, y) with boundary checks."""
    width, height = image.size
    if x < 0 or x >= width or y < 0 or y >= height:
        return (0, 0, 0, 0) if image.mode == 'RGBA' else (0, 0, 0)
    return image.getpixel((x, y))

def pix_avg(img_path, output_path=None):
    """Adjust pixels to the average of adjacent ones."""
    def average_adjacent_pixels(image):
        width, height = image.size
        new_image = Image.new(image.mode, (width, height))
        for y in tqdm(range(height), desc="Processing rows for pix_avg"):
            for x in range(width):
                neighbors = [
                    get_pixel(image, x, y),
                    get_pixel(image, x - 1, y),
                    get_pixel(image, x + 1, y),
                    get_pixel(image, x, y - 1),
                    get_pixel(image, x, y + 1),
                    get_pixel(image, x - 2, y),
                    get_pixel(image, x + 2, y),
                    get_pixel(image, x, y - 2),
                    get_pixel(image, x, y + 2),
                ]
                ran_avg = random.randint(0, 3)
                if image.mode == 'RGBA':
                    r, g, b, a = zip(*neighbors[:4 + ran_avg * 4])
                    r = sum(r) // len(r)
                    g = sum(g) // len(g)
                    b = sum(b) // len(b)
                    a = sum(a) // len(a)
                    new_image.putpixel((x, y), (r, g, b, a))
                else:
                    r, g, b = zip(*neighbors[:4 + ran_avg * 4])
                    r = sum(r) // len(r)
                    g = sum(g) // len(g)
                    b = sum(b) // len(b)
                    new_image.putpixel((x, y), (r, g, b))
        return new_image

    try:
        image = Image.open(img_path)
        if output_path is None:
            output_path = os.path.join(os.path.dirname(img_path), "adjusted_image_avg.jpg")
        adjusted_image = average_adjacent_pixels(image)
        # Convert to RGB if the image is in a mode incompatible with JPG
        if adjusted_image.mode in ("RGBA", "P"):
            adjusted_image = adjusted_image.convert("RGB")
        adjusted_image.save(output_path, "JPEG")
        print(f"Saved averaged image to {output_path}")
    except Exception as e:
        print(f"Error in pix_avg: {e}")

def cshading(img_path, output_path=None):
    """Adjust pixels to the closest color in a predefined palette."""
    colors = [(r, g, b) for r in range(0, 256, 51) for g in range(0, 256, 51) for b in range(0, 256, 51)]

    def cell_shader(R, G, B):
        return min(colors, key=lambda color: abs(color[0] - R) + abs(color[1] - G) + abs(color[2] - B))

    def get_new_image(image):
        width, height = image.size
        new_image = Image.new(image.mode, (width, height))
        for y in tqdm(range(height), desc="Processing rows for cshading"):
            for x in range(width):
                pixel = get_pixel(image, x, y)
                if image.mode == 'RGBA':
                    r, g, b, a = pixel
                    r, g, b = cell_shader(r, g, b)
                    new_image.putpixel((x, y), (r, g, b, a))
                else:
                    r, g, b = pixel
                    r, g, b = cell_shader(r, g, b)
                    new_image.putpixel((x, y), (r, g, b))
        return new_image

    try:
        image = Image.open(img_path)
        if output_path is None:
            output_path = os.path.join(os.path.dirname(img_path), "adjusted_image_shaded.jpg")
        adjusted_image = get_new_image(image)
        adjusted_image.save(output_path)
        print(f"Saved shaded image to {output_path}")
    except Exception as e:
        print(f"Error in cshading: {e}")

def final_filter(img_path, output_path=None):
    """Apply the final filter from canvas.py."""
    def average_adjacent_pixels(image):
        width, height = image.size
        new_image = Image.new(image.mode, (width, height))
        for y in range(height):
            for x in range(width):
                if image.mode == 'RGBA':
                    r, g, b, a = get_pixel(image, x, y)
                    if(y % 2 == 1 and x % 2 == 1):
                        r -= 10
                        g -= 10
                        b -= 10
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))
                    new_image.putpixel((x, y), (r, g, b, a))
                else:
                    r, g, b = get_pixel(image, x, y)
                    if(y % 2 == 1 and x % 2 == 1):
                        r -= 10
                        g -= 10
                        b -= 10
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))
                    new_image.putpixel((x, y), (r, g, b))
        return new_image

    try:
        image = Image.open(img_path)
        if output_path is None:
            output_path = os.path.join(os.path.dirname(img_path), "final_adjusted_image.jpg")
        adjusted_image = average_adjacent_pixels(image)
        adjusted_image.save(output_path, "JPEG")
        print(f"Saved final adjusted image to {output_path}")
    except Exception as e:
        print(f"Error in final_filter: {e}")

if __name__ == "__main__":
    try:
        gimg = input("ABS Path to Image: ")
        avg_output_path = os.path.join(os.path.dirname(gimg), "adjusted_image_avg.jpg")
        shaded_output_path = os.path.join(os.path.dirname(gimg), "adjusted_image_shaded.jpg")
        final_output_path = os.path.join(os.path.dirname(gimg), "final_adjusted_image.jpg")
        
        # Generate the averaged image
        pix_avg(gimg, avg_output_path)
        
        # Generate the shaded image
        cshading(avg_output_path, shaded_output_path)
        
        # Apply the final filter
        final_filter(shaded_output_path, final_output_path)
        
        # Delete the intermediate files
        if os.path.exists(avg_output_path):
            os.remove(avg_output_path)
            print(f"Deleted intermediate file: {avg_output_path}")
        if os.path.exists(shaded_output_path):
            os.remove(shaded_output_path)
            print(f"Deleted intermediate file: {shaded_output_path}")
    except Exception as e:
        print(f"Error in main execution: {e}")