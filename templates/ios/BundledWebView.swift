import UIKit
import WebKit

// Original generic host. No private WebKit settings, network server, or native bridge.
final class BundledWebViewController: UIViewController, WKNavigationDelegate, WKUIDelegate {
    private(set) var webView: WKWebView!
    private(set) var webRoot: URL!

    static func permits(_ url: URL, inside root: URL) -> Bool {
        guard url.isFileURL, url.host == nil || url.host == "" || url.host == "localhost",
              url.user == nil, url.password == nil, url.port == nil, url.query == nil else { return false }
        // Only the landing document may navigate. Bundle resources are loaded as
        // subresources under the separate read-access and content-security policy.
        let entry = root.resolvingSymlinksInPath().standardizedFileURL.appendingPathComponent("index.html").path
        let path = url.resolvingSymlinksInPath().standardizedFileURL.path
        return path == entry
    }

    override func loadView() {
        guard let root = Bundle.main.resourceURL?.appendingPathComponent("Web", isDirectory: true),
              FileManager.default.fileExists(atPath: root.appendingPathComponent("index.html").path) else {
            let label = UILabel()
            label.text = "Bundled app files are unavailable."
            label.numberOfLines = 0
            view = label
            return
        }
        webRoot = root
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.preferences.javaScriptCanOpenWindowsAutomatically = false
        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsLinkPreview = false
        view = webView
        webView.loadFileURL(root.appendingPathComponent("index.html"), allowingReadAccessTo: root)
    }

    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard action.targetFrame?.isMainFrame == true, !action.shouldPerformDownload,
              let url = action.request.url, Self.permits(url, inside: webRoot) else {
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, decidePolicyFor response: WKNavigationResponse,
                 decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
        guard response.isForMainFrame, response.canShowMIMEType,
              let url = response.response.url, Self.permits(url, inside: webRoot) else {
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        return nil
    }
}
