package coden.journal.notion

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class NotionPathTest{

    @Test
    fun path() {
        assertEquals("Test Table", NotionPath("/Other/Test Table").title())
        assertEquals("/Other/Test Table", NotionPath("/Other/Test Table").path())
        assertEquals(NotionPath("/Other/"), NotionPath("/Other/Test Table").parent())
        assertEquals(null, NotionPath("/Other").parent())
        assertTrue(NotionPath("/Other").isTopLevel())
        assertEquals(null, NotionPath("/Junit Test").parent())
        assertEquals(listOf(
            NotionPath("/Other/Another/"),
            NotionPath("/Other")
        ),
            NotionPath("/Other/Another/Test Table").parents())
        assertTrue(NotionPath("/Hallo").isTopLevel())
        assertTrue(NotionPath("/ThisIs Page").isTopLevel())
    }
}