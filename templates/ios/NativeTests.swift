import XCTest
import WebKit
@testable import GeneratedApp

@MainActor
final class NativeTests: XCTestCase {
    func testNavigationBoundary() throws {
        let root = URL(fileURLWithPath: "/tmp/bundle/Web", isDirectory: true)
        XCTAssertTrue(BundledWebViewController.permits(root.appendingPathComponent("index.html"), inside: root))
        XCTAssertTrue(BundledWebViewController.permits(try XCTUnwrap(URL(string: "file:///tmp/bundle/Web/index.html#recap")), inside: root))
        for text in ["https://example.invalid/", "javascript:alert(1)", "data:text/html,hello",
                     "file:///tmp/bundle/Web-other/index.html", "file:///tmp/bundle/Web/../secret",
                     "file:///tmp/bundle/Web/app.mjs", "file:///tmp/bundle/Web/nested/index.html",
                     "file:///tmp/bundle/Web/%2e%2e/secret", "file:///tmp/bundle/Web/index.html?redirect=1",
                     "file://otherhost/tmp/bundle/Web/index.html"] {
            XCTAssertFalse(BundledWebViewController.permits(try XCTUnwrap(URL(string: text)), inside: root), text)
        }
    }

    func testLandingDocumentSymlinkCannotEscapeBundle() throws {
        let scratch = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        let root = scratch.appendingPathComponent("Web", isDirectory: true)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: scratch) }
        let outside = scratch.appendingPathComponent("outside.html")
        try Data("outside".utf8).write(to: outside)
        let entry = root.appendingPathComponent("index.html")
        try FileManager.default.createSymbolicLink(at: entry, withDestinationURL: outside)
        XCTAssertFalse(BundledWebViewController.permits(entry, inside: root))
    }

    private func readyHost() async throws -> BundledWebViewController {
        let host = BundledWebViewController()
        host.loadViewIfNeeded()
        let web = try XCTUnwrap(host.webView)
        for _ in 0..<100 {
            if let ready = try? await web.evaluateJavaScript("Boolean(document.querySelector('#players'))"),
               (ready as? Bool) == true { return host }
            try await Task.sleep(nanoseconds: 100_000_000)
        }
        let diagnostic = try? await web.evaluateJavaScript("JSON.stringify({url: location.href, ready: document.readyState, secure: isSecureContext, locks: Boolean(navigator.locks), screen: document.querySelector('#screen')?.textContent, warning: document.querySelector('#warning')?.textContent, title: document.title})")
        XCTFail("Bundled startup did not reach setup; do not bypass WebKit security settings. Diagnostic: \(String(describing: diagnostic))")
        throw NSError(domain: "NativeFeasibility", code: 1)
    }

    func testBundledModulesWebLocksAndPersistentStore() async throws {
        let host = try await readyHost()
        let web = try XCTUnwrap(host.webView)
        let locks = try await web.evaluateJavaScript("Boolean(navigator.locks && navigator.locks.request)")
        XCTAssertEqual(locks as? Bool, true, "Missing Web Locks is a stop gate, not permission to weaken writes.")
        XCTAssertTrue(web.configuration.websiteDataStore.isPersistent)
        let probe = "factory.native-test." + UUID().uuidString
        let result = try await web.callAsyncJavaScript(
            "const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 3000); try { return await navigator.locks.request(key, {signal: controller.signal}, () => { localStorage.setItem(key, 'persisted'); return localStorage.getItem(key); }); } finally { clearTimeout(timer); }",
            arguments: ["key": probe], in: nil, contentWorld: .page)
        XCTAssertEqual(result as? String, "persisted")
        let second = try await readyHost()
        XCTAssertFalse(web === second.webView)
        let restored = try await second.webView.callAsyncJavaScript(
            "const value = localStorage.getItem(key); localStorage.removeItem(key); return value;",
            arguments: ["key": probe], in: nil, contentWorld: .page)
        XCTAssertEqual(restored as? String, "persisted")
        // Process termination/relaunch and complete-game UI coverage remain separate gates.
    }
}
