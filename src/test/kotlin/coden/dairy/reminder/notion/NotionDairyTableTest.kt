package coden.dairy.reminder.notion

import coden.dairy.reminder.model.DairyEntry
import coden.dairy.reminder.model.DairyRepository
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.create
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.exists
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.get
import coden.dairy.reminder.notion.NotionDairyTableUtility.Companion.purge
import notion.api.v1.NotionClient
import notion.api.v1.request.search.SearchRequest
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation

import org.junit.jupiter.api.extension.ExtendWith
import java.time.LocalDate

@TestMethodOrder(OrderAnnotation::class)
class NotionDairyTableTest {

    private val token = "secret_onegyirr9ANiY7fs3lp5uUjNjXuehh8AxrIzbVdPNGJ"
    private val notion = NotionClient(token)
    private val path = NotionPath("/Junit Test/Junit Table")

    lateinit var db: DairyRepository


    @BeforeEach
    fun create() {
        db = notion.get(path)
        db.clear()
    }

    @Test
    @Order(0)
    fun entries() {
        assertTrue(db.entries().isEmpty())
    }

    @Test
    @Order(1)
    fun insert() {
        val month = LocalDate.now().withDayOfMonth(1)
        val expected = DairyEntry(month, "Very good")
        db.insert(expected)
        val entries = db.entries()
        assertEquals(1, entries.size)
        assertEquals(expected, entries.first())
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
    fun clear() {
        db.insert(DairyEntry(LocalDate.now(), "Alright"))
        db.insert(DairyEntry(LocalDate.now(), "Ok"))
        db.clear()
        assertTrue(db.entries().isEmpty())
    }


    @Test
    fun delete() {
    }

}