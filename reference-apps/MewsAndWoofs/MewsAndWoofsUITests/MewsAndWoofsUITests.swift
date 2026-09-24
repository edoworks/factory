import XCTest

@MainActor
final class MewsAndWoofsUITests: XCTestCase {
    override func setUp() {
        continueAfterFailure = false
    }

    func testWelcomeExplainsPremiseAndOpensDemo() {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.buttons["demoMomentButton"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["premiseDisclosure"].exists)
        app.buttons["demoMomentButton"].tap()
        XCTAssertTrue(element(app, "momentCanvas").waitForExistence(timeout: 5))
    }

    func testContextBubbleControlsAndPreview() {
        let app = XCUIApplication()
        app.launchArguments = ["-UITestDemoEditor"]
        app.launch()

        XCTAssertTrue(element(app, "momentCanvas").waitForExistence(timeout: 5))
        app.buttons["context-playtime"].tap()
        XCTAssertTrue(app.buttons["context-playtime"].isSelected)
        app.buttons["Moveright"].tap()
        if !app.buttons["Makelarger"].exists {
            app.swipeUp()
        }
        app.buttons["Makelarger"].tap()
        app.buttons["Resetbubble"].tap()
        app.buttons["previewButton"].tap()
        XCTAssertTrue(element(app, "previewCanvas").waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["editButton"].exists)
    }

    func testEditorVisualEvidence() {
        let app = XCUIApplication()
        app.launchArguments = ["-UITestDemoEditor"]
        app.launch()
        XCTAssertTrue(element(app, "momentCanvas").waitForExistence(timeout: 5))

        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "mews-woofs-editor"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func testPreviewVisualEvidence() {
        let app = XCUIApplication()
        app.launchArguments = ["-UITestPreview"]
        app.launch()
        XCTAssertTrue(element(app, "previewCanvas").waitForExistence(timeout: 5))

        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "mews-woofs-preview"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func testAccessibilityTextSizeKeepsPrimaryJourneyAvailable() {
        let app = XCUIApplication()
        app.launchArguments = [
            "-UITestDemoEditor",
            "-UIPreferredContentSizeCategoryName",
            "UICTContentSizeCategoryAccessibilityXXXL",
        ]
        app.launch()

        XCTAssertTrue(element(app, "momentCanvas").waitForExistence(timeout: 5))
        let preview = app.buttons["previewButton"]
        if !preview.isHittable {
            app.swipeUp()
        }
        XCTAssertTrue(preview.waitForExistence(timeout: 5))
        preview.tap()
        XCTAssertTrue(element(app, "previewCanvas").waitForExistence(timeout: 5))
    }

    private func element(_ app: XCUIApplication, _ identifier: String) -> XCUIElement {
        app.descendants(matching: .any).matching(identifier: identifier).firstMatch
    }
}
