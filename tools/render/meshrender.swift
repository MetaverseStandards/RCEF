// SPDX-License-Identifier: MIT
// Copyright (c) 2026 RCEF contributors. Written for RCEF's face renders; see tools/render/README.md.
// meshrender: offscreen SceneKit renderer for plain triangle meshes.
// Usage: meshrender jobs.json
// jobs.json: {"width":W,"height":H,"jobs":[{"positions":"p.f32","indices":"i.u32",
//   "colors":"c.f32" (optional, per-vertex RGB float32), "lit":true, "color":[r,g,b],
//   "background":[r,g,b], "camera":{"position":[x,y,z],"target":[x,y,z],"up":[0,1,0],"yfov":deg},
//   "out":"frame.png"}]}
// Positions are little-endian float32 xyz triples, indices uint32 triangle lists.
import AppKit
import Foundation
import Metal
import SceneKit

struct Camera: Decodable { let position: [Float]; let target: [Float]; let up: [Float]; let yfov: Double }
struct Job: Decodable {
    let positions: String; let indices: String; let colors: String?
    let lit: Bool?; let color: [Double]?; let background: [Double]?
    let camera: Camera; let out: String
}
struct Batch: Decodable { let width: Int; let height: Int; let jobs: [Job] }

func readArray<T>(_ path: String, _: T.Type) throws -> [T] {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    return data.withUnsafeBytes { Array($0.bindMemory(to: T.self)) }
}
func v3(_ a: [Float]) -> SCNVector3 { SCNVector3(CGFloat(a[0]), CGFloat(a[1]), CGFloat(a[2])) }
func rgb(_ c: [Double]) -> NSColor { NSColor(srgbRed: c[0], green: c[1], blue: c[2], alpha: 1) }

func vertexNormals(_ p: [Float], _ idx: [UInt32]) -> [SCNVector3] {
    var n = [SIMD3<Float>](repeating: .zero, count: p.count / 3)
    func at(_ i: UInt32) -> SIMD3<Float> { let k = Int(i) * 3; return SIMD3(p[k], p[k + 1], p[k + 2]) }
    for t in stride(from: 0, to: idx.count, by: 3) {
        let face = simd_cross(at(idx[t + 1]) - at(idx[t]), at(idx[t + 2]) - at(idx[t]))  // area-weighted
        for k in 0..<3 { n[Int(idx[t + k])] += face }
    }
    return n.map { let l = simd_length($0); let u = l > 0 ? $0 / l : SIMD3<Float>(0, 1, 0)
        return SCNVector3(CGFloat(u.x), CGFloat(u.y), CGFloat(u.z)) }
}

func render(_ job: Job, _ renderer: SCNRenderer, _ size: CGSize) throws {
    let p = try readArray(job.positions, Float.self)
    let idx = try readArray(job.indices, UInt32.self)
    let verts = stride(from: 0, to: p.count, by: 3).map { SCNVector3(CGFloat(p[$0]), CGFloat(p[$0 + 1]), CGFloat(p[$0 + 2])) }
    var sources = [SCNGeometrySource(vertices: verts), SCNGeometrySource(normals: vertexNormals(p, idx))]
    if let cpath = job.colors {
        let c = try readArray(cpath, Float.self)
        let data = c.withUnsafeBufferPointer { Data(buffer: $0) }
        sources.append(SCNGeometrySource(data: data, semantic: .color, vectorCount: c.count / 3,
                                         usesFloatComponents: true, componentsPerVector: 3,
                                         bytesPerComponent: 4, dataOffset: 0, dataStride: 12))
    }
    let element = SCNGeometryElement(indices: idx, primitiveType: .triangles)
    let geometry = SCNGeometry(sources: sources, elements: [element])
    let material = SCNMaterial()
    material.isDoubleSided = true
    material.diffuse.contents = job.colors == nil ? rgb(job.color ?? [0.75, 0.75, 0.78]) : NSColor.white
    material.lightingModel = (job.lit ?? true) ? .lambert : .constant
    geometry.materials = [material]

    let scene = SCNScene()
    scene.background.contents = rgb(job.background ?? [0.12, 0.12, 0.14])
    scene.rootNode.addChildNode(SCNNode(geometry: geometry))
    let cam = SCNCamera()
    cam.fieldOfView = CGFloat(job.camera.yfov)
    cam.projectionDirection = .vertical
    cam.automaticallyAdjustsZRange = true
    let camNode = SCNNode()
    camNode.camera = cam
    camNode.position = v3(job.camera.position)
    camNode.look(at: v3(job.camera.target), up: v3(job.camera.up), localFront: SCNVector3(0, 0, -1))
    scene.rootNode.addChildNode(camNode)
    let key = SCNNode(); key.light = SCNLight(); key.light!.type = .directional; key.light!.intensity = 900
    camNode.addChildNode(key)  // headlight: lighting follows the view
    key.eulerAngles = SCNVector3(-0.35, -0.35, 0)
    let fill = SCNNode(); fill.light = SCNLight(); fill.light!.type = .ambient; fill.light!.intensity = 300
    scene.rootNode.addChildNode(fill)

    renderer.scene = scene
    renderer.pointOfView = camNode
    let image = renderer.snapshot(atTime: 0, with: size, antialiasingMode: .multisampling4X)
    guard let tiff = image.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else {
        throw NSError(domain: "meshrender", code: 2, userInfo: [NSLocalizedDescriptionKey: "PNG encode failed"])
    }
    try png.write(to: URL(fileURLWithPath: job.out))
}

guard CommandLine.arguments.count == 2 else { FileHandle.standardError.write("usage: meshrender jobs.json\n".data(using: .utf8)!); exit(64) }
do {
    let batch = try JSONDecoder().decode(Batch.self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1])))
    guard let device = MTLCreateSystemDefaultDevice() else { throw NSError(domain: "meshrender", code: 1, userInfo: [NSLocalizedDescriptionKey: "no Metal device"]) }
    let renderer = SCNRenderer(device: device, options: nil)
    let size = CGSize(width: batch.width, height: batch.height)
    for job in batch.jobs { try autoreleasepool { try render(job, renderer, size) } }
    print("rendered \(batch.jobs.count) images")
} catch { FileHandle.standardError.write("meshrender error: \(error)\n".data(using: .utf8)!); exit(1) }
