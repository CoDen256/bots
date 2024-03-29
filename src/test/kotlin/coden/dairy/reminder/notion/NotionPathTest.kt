package coden.dairy.reminder.notion

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class NotionPathTest{

    @Test
    fun path() {
        assertEquals("Test Table", NotionPath("/Other/Test Table").filename())
        assertEquals("\\Other\\Test Table", NotionPath("/Other/Test Table").path())
        assertEquals(NotionPath("/Other/"), NotionPath("/Other/Test Table").parent())
        assertEquals(NotionPath("/"), NotionPath("/Other").parent())
        assertEquals(null, NotionPath("/").parent())
        assertEquals(listOf(
            NotionPath("/Other/Another/"),
            NotionPath("/Other"),
            NotionPath("/")),
            NotionPath("/Other/Another/Test Table").parents())
        assertTrue(NotionPath("/").isRoot())
        assertTrue(NotionPath("/").isRoot())
    }
}