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

    private func readyHost(waitForApp: Bool = true) async throws -> BundledWebViewController {
        let host = BundledWebViewController()
        host.loadViewIfNeeded()
        let web = try XCTUnwrap(host.webView)
        for _ in 0..<100 {
            let condition = waitForApp ? "Boolean(document.querySelector('#players'))" : "document.readyState === 'complete' && location.protocol === 'file:'"
            if let ready = try? await web.evaluateJavaScript(condition),
               (ready as? Bool) == true { return host }
            try await Task.sleep(nanoseconds: 100_000_000)
        }
        let diagnostic = try? await web.evaluateJavaScript("JSON.stringify({url: location.href, ready: document.readyState, secure: isSecureContext, locks: Boolean(navigator.locks), screen: document.querySelector('#screen')?.textContent, warning: document.querySelector('#warning')?.textContent, title: document.title})")
        XCTFail("Bundled startup did not reach setup; do not bypass WebKit security settings. Diagnostic: \(String(describing: diagnostic))")
        throw NSError(domain: "NativeFeasibility", code: 1)
    }

    func testBundledScriptWebLocksAndPersistentStore() async throws {
        let host = try await readyHost()
        try await checkStorage(host, waitForApp: true)
    }

    func testCompleteSpecDrivenGameAndReload() async throws {
        let host = try await readyHost()
        let url = try XCTUnwrap(Bundle.main.url(forResource: "spec", withExtension: "mjs", subdirectory: "Web"))
        let line = try String(contentsOf: url, encoding: .utf8).components(separatedBy: "\n")[1]
        let json = String(line.dropFirst("export const spec = ".count).dropLast())
        let spec = try JSONSerialization.jsonObject(with: Data(json.utf8))
        let value = try await host.webView.callAsyncJavaScript("""
        const wait = async predicate => { for(let i=0;i<100;i++){if(predicate())return;await new Promise(r=>setTimeout(r,50));}throw new Error('Native DOM wait timed out: '+document.querySelector('#warning').textContent); };
        const click = id => document.querySelector(id).click();
        document.querySelector('#setup').requestSubmit();
        await wait(()=>document.querySelector('#player-0'));
        for(const stage of definition.stages){
          if(stage.kind==='lock'){
            for(let player=0;player<2;player++){
              click('#player-'+player);
              const form=document.querySelector('#picks');
              for(const id of stage.questions)form.elements.namedItem('answer:'+id).value=definition.questions.find(q=>q.id===id).options[0].id;
              if(stage.boost)form.elements.namedItem('control:boost').value=stage.questions[0];
              form.requestSubmit();await wait(()=>!document.querySelector('#picks'));
            }
          }else{
            const form=document.querySelector('#results');
            for(const id of stage.questions)form.elements.namedItem('answer:'+id).value=definition.questions.find(q=>q.id===id).options[0].id;
            const before=localStorage.getItem('factory.game.'+definition.id);
            form.requestSubmit();
            if(localStorage.getItem('factory.game.'+definition.id)!==before)throw new Error('Preview mutated persistence');
            click('#confirm');await wait(()=>!document.querySelector('#confirm'));
          }
        }
        const expected=definition.questions.reduce((n,q)=>n+q.points,0)+definition.stages.filter(s=>s.boost).reduce((n,s)=>n+definition.questions.find(q=>q.id===s.questions[0]).points,0);
        const scores=[...document.querySelectorAll('.score')].map(n=>n.textContent);
        if(scores.length!==2||scores.some(s=>s!==expected+' prediction points'))throw new Error('Unexpected final scores: '+scores);
        if([...document.querySelectorAll('#recap h3')].some(n=>!n.textContent.startsWith('#1 ')))throw new Error('Shared ranks lost');
        return localStorage.getItem('factory.game.'+definition.id);
        """, arguments: ["definition": spec], in: nil, contentWorld: .page)
        let saved = try XCTUnwrap(value as? String)
        XCTAssertFalse(saved.isEmpty)
        host.webView.reload()
        for _ in 0..<100 {
            if (try? await host.webView.evaluateJavaScript("document.querySelector('#screen h2')?.textContent === 'Final podium'")) as? Bool == true { break }
            try await Task.sleep(nanoseconds: 50_000_000)
        }
        let restored = try await host.webView.callAsyncJavaScript("return localStorage.getItem('factory.game.'+definition.id)", arguments: ["definition": spec], in: nil, contentWorld: .page)
        XCTAssertEqual(restored as? String, saved)
        let podium = try await host.webView.evaluateJavaScript("document.querySelector('#screen h2')?.textContent")
        XCTAssertEqual(podium as? String, "Final podium")
        _ = try await host.webView.evaluateJavaScript("document.querySelector('#reset').click();document.querySelector('#confirm-reset').click()")
        for _ in 0..<100 {
            if (try? await host.webView.evaluateJavaScript("Boolean(document.querySelector('#players'))")) as? Bool == true { return }
            try await Task.sleep(nanoseconds: 50_000_000)
        }
        XCTFail("Synthetic match reset did not finish")
    }

    private func checkStorage(_ host: BundledWebViewController, waitForApp: Bool) async throws {
        let web = try XCTUnwrap(host.webView)
        let locks = try await web.evaluateJavaScript("Boolean(navigator.locks && navigator.locks.request)")
        XCTAssertEqual(locks as? Bool, true, "Missing Web Locks is a stop gate, not permission to weaken writes.")
        XCTAssertTrue(web.configuration.websiteDataStore.isPersistent)
        let probe = "factory.native-test." + UUID().uuidString
        let result = try await web.callAsyncJavaScript(
            "const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 3000); try { return await navigator.locks.request(key, {signal: controller.signal}, () => { localStorage.setItem(key, 'persisted'); return localStorage.getItem(key); }); } finally { clearTimeout(timer); }",
            arguments: ["key": probe], in: nil, contentWorld: .page)
        XCTAssertEqual(result as? String, "persisted")
        let second = try await readyHost(waitForApp: waitForApp)
        XCTAssertFalse(web === second.webView)
        let restored = try await second.webView.callAsyncJavaScript(
            "const value = localStorage.getItem(key); localStorage.removeItem(key); return value;",
            arguments: ["key": probe], in: nil, contentWorld: .page)
        XCTAssertEqual(restored as? String, "persisted")
        // Process termination/relaunch and complete-game UI coverage remain separate gates.
    }
}
