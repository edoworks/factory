import XCTest

final class AppTemplateUITests: XCTestCase {
    override func setUp() {
        continueAfterFailure = false
    }

    func testAppLaunches() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.navigationBars["AppTemplate"].waitForExistence(timeout: 5))
    }

    func testEmptyStateShowsOnLaunch() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["No items yet"].waitForExistence(timeout: 5))
    }

    func testAddItemFlow() {
        let app = XCUIApplication()
        app.launch()

        // Tap add button
        app.buttons["Add Item"].tap()

        // Type text
        app.textFields["Enter item text"].tap()
        app.textFields["Enter item text"].typeText("My first item")

        // Confirm
        app.buttons["Add"].tap()

        // Verify item appears
        XCTAssertTrue(app.staticTexts["My first item"].waitForExistence(timeout: 5))
    }
}