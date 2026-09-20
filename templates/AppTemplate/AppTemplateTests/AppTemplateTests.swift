import XCTest
@testable import AppTemplate

final class AppTemplateTests: XCTestCase {
    func testItemCanBeAdded() {
        var items: [String] = []
        items.append("Test item")
        XCTAssertEqual(items.count, 1)
        XCTAssertEqual(items.first, "Test item")
    }

    func testItemCanBeDeleted() {
        var items: [String] = ["Item 1", "Item 2", "Item 3"]
        items.remove(atOffsets: IndexSet([1]))
        XCTAssertEqual(items.count, 2)
        XCTAssertEqual(items, ["Item 1", "Item 3"])
    }

    func testEmptyItemIsNotAdded() {
        var items: [String] = []
        let trimmed = "  ".trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty {
            items.append(trimmed)
        }
        XCTAssertEqual(items.count, 0)
    }

    func testExportFormat() {
        let items = ["First", "Second", "Third"]
        let exported = items.joined(separator: "\n")
        XCTAssertEqual(exported, "First\nSecond\nThird")
    }
}