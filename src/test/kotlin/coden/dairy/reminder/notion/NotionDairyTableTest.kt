package coden.dairy.reminder.notion

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
    private val repository: NotionDairyTable = NotionDairyTable(notion, path)


    @Test
    @Order(0)
    fun create() {
        repository.create()
        assertTrue(repository.exists())
        assertTrue(notion.search(
            path.filename(),
            filter = SearchRequest.SearchFilter("database", property = "object"))
            .results
            .any { it.asDatabase().title?.any { it.plainText == path.filename() } == true })
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
        repository.purge()
        assertFalse(repository.exists())
        assertTrue(notion.search(
            path.filename(),
            filter = SearchRequest.SearchFilter("database", property = "object"))
            .results
            .none { it.asDatabase().title?.any { it.plainText == path.filename() } == true })
    }
}