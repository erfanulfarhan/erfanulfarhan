// Cut-out mask and face box for scripts/make_portrait.py, using Apple's Vision.
//
//     swiftc -O scripts/person_mask.swift -o /tmp/person_mask
//     /tmp/person_mask photo.jpg mask.png    ->  prints {"face":[x,y,w,h]} (pixels, top-left origin)
//
// The mask is the union of Vision's person segmentation and its foreground instance mask, at
// the photo's own size: the person model alone can drop dark hair against a dark background,
// the foreground model alone can take in a chair back. macOS only; the daily job never needs it.
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count == 3,
      let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    FileHandle.standardError.write("usage: person_mask <photo> <mask.png>\n".data(using: .utf8)!); exit(2)
}
let W = CGFloat(img.width), H = CGFloat(img.height)
let handler = VNImageRequestHandler(cgImage: img, orientation: .up, options: [:])
let seg = VNGeneratePersonSegmentationRequest()
seg.qualityLevel = .accurate
seg.outputPixelFormat = kCVPixelFormatType_OneComponent8
let fg = VNGenerateForegroundInstanceMaskRequest()
let faces = VNDetectFaceRectanglesRequest()
try handler.perform([seg, fg, faces])

let ctx = CIContext()
func scaled(_ ci: CIImage) -> CIImage {
    ci.transformed(by: CGAffineTransform(scaleX: W / ci.extent.width, y: H / ci.extent.height))
}
var mask: CIImage? = nil
if let buf = seg.results?.first?.pixelBuffer { mask = scaled(CIImage(cvPixelBuffer: buf)) }
if let obs = fg.results?.first,
   let buf = try? obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler) {
    let m = CIImage(cvPixelBuffer: buf)
    mask = mask.map { m.applyingFilter("CIMaximumCompositing", parameters: [kCIInputBackgroundImageKey: $0]) } ?? m
}
guard let out = mask,
      let cg = ctx.createCGImage(out, from: CGRect(x: 0, y: 0, width: W, height: H), format: .L8,
                                 colorSpace: CGColorSpaceCreateDeviceGray()),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: args[2]) as CFURL,
                                                 UTType.png.identifier as CFString, 1, nil) else {
    FileHandle.standardError.write("no person found\n".data(using: .utf8)!); exit(1)
}
CGImageDestinationAddImage(dest, cg, nil)
CGImageDestinationFinalize(dest)
let f = (faces.results ?? []).max { $0.boundingBox.width < $1.boundingBox.width }?.boundingBox ?? .zero
print("{\"face\":[\(Int(f.minX * W)),\(Int((1 - f.maxY) * H)),\(Int(f.width * W)),\(Int(f.height * H))]}")
