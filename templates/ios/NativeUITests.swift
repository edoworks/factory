import XCTest

final class NativeUITests: XCTestCase {
    func testSavedMatchSurvivesProcessTerminationAndRelaunch() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.buttons["Reset this match"].waitForExistence(timeout: 15))
        app.buttons["Reset this match"].tap()
        app.buttons["Confirm reset"].tap()
        XCTAssertTrue(app.buttons["Start rehearsal"].waitForExistence(timeout: 5))
        app.buttons["Start rehearsal"].tap()
        let firstCard = app.buttons["Open Player 1’s card"]
        XCTAssertTrue(firstCard.waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["Open Player 2’s card"].exists)
        app.terminate()
        XCTAssertEqual(app.state, .notRunning)
        app.launch()
        XCTAssertTrue(firstCard.waitForExistence(timeout: 15))
        XCTAssertTrue(app.buttons["Open Player 2’s card"].exists)
        XCTAssertFalse(app.buttons["Start rehearsal"].exists)
        // Preserve unrelated storage; clear only this synthetic test's match.
        app.buttons["Reset this match"].tap()
        app.buttons["Confirm reset"].tap()
        XCTAssertTrue(app.buttons["Start rehearsal"].waitForExistence(timeout: 5))
    }
}
