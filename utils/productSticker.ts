const stickers = new Map<string, Promise<HTMLCanvasElement>>()

// Trim transparent padding when rendering official pack shots as physics stickers.
// Source assets remain unchanged; cache the small canvas shared by spawned items.
export function loadProductSticker(src: string): Promise<HTMLCanvasElement> {
  if (!stickers.has(src)) stickers.set(src, (async () => {
    const image = new Image()
    image.src = src
    await image.decode()
    const source = document.createElement('canvas')
    source.width = image.naturalWidth
    source.height = image.naturalHeight
    const context = source.getContext('2d')!
    context.drawImage(image, 0, 0)
    const { data } = context.getImageData(0, 0, source.width, source.height)
    let left = source.width, top = source.height, right = 0, bottom = 0
    for (let y = 0; y < source.height; y++) for (let x = 0; x < source.width; x++) {
      if (data[(y * source.width + x) * 4 + 3] > 24) {
        left = Math.min(left, x); top = Math.min(top, y)
        right = Math.max(right, x); bottom = Math.max(bottom, y)
      }
    }
    if (right < left || bottom < top) return source
    const width = right - left + 1, height = bottom - top + 1
    const scale = Math.min(1, 512 / Math.max(width, height))
    const cropped = document.createElement('canvas')
    cropped.width = Math.max(1, Math.round(width * scale))
    cropped.height = Math.max(1, Math.round(height * scale))
    cropped.getContext('2d')!.drawImage(source, left, top, width, height, 0, 0, cropped.width, cropped.height)
    return cropped
  })())
  return stickers.get(src)!
}
