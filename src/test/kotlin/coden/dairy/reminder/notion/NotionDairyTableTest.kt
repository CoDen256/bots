package coden.dairy.reminder.notion

import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.create
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.exists
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.purge
import notion.api.v1.NotionClient
import notion.api.v1.request.search.SearchRequest
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Order

import org.junit.jupiter.api.Test

class NotionDairyTableTest {

    private val token = "secret_onegyirr9ANiY7fs3lp5uUjNjXuehh8AxrIzbVdPNGJ"
    private val notion = NotionClient(token)
    private val path = NotionPath("/Junit Test/Junit Table")

    @Test
    @Order(0)
    fun create() {
        notion.create(path)
        assertTrue(notion.exists(path))
        assertTrue(notion.search(
            path.title(),
            filter = SearchRequest.SearchFilter("database", property = "object"))
            .results
            .any { it.asDatabase().title?.any { it.plainText == path.title() } == true })
    }

    @Test
    fun entries() {
    }

    @Test
    fun get() {
    }

    @Test
    fun first() {
    }

    @Test
    fun last() {
    }

    @Test
    fun insert() {
    }







    @Test
    fun clear() {
    }

    @Test
    fun close() {
    }

    @Test
    fun delete() {
    }

    @Test
    @Order(Int.MAX_VALUE)
    fun purge() {
        notion.purge(path)
        assertFalse(notion.exists(path))
        assertTrue(notion.search(
            path.title(),
            filter = SearchRequest.SearchFilter("database", property = "object"))
            .results
            .none { it.asDatabase().title?.any { it.plainText == path.title() } == true })
    }
}