package coden.dairy.reminder.notion

import coden.dairy.reminder.model.DairyRepository
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.create
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.exists
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.get
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.purge
import notion.api.v1.NotionClient
import notion.api.v1.request.search.SearchRequest
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Order

import org.junit.jupiter.api.Test

class NotionDairyTableTest {

    private val token = "secret_onegyirr9ANiY7fs3lp5uUjNjXuehh8AxrIzbVdPNGJ"
    private val notion = NotionClient(token)
    private val path = NotionPath("/Junit Test/Junit Table")

    lateinit var db: DairyRepository


    @BeforeEach
    fun create() {
        db = notion.get(path)
    }

    @Test
    fun entries() {
        assertTrue(db.entries().isEmpty())
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

}