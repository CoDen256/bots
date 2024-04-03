package coden.journal.reminder.notion

import coden.journal.reminder.core.DairyEntry
import coden.journal.reminder.core.DairyRepository
import coden.journal.reminder.notion.NotionDairyTableUtility.Companion.get
import notion.api.v1.NotionClient
import notion.api.v1.http.OkHttp4Client
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation
import org.junit.jupiter.api.Order
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestMethodOrder
import java.time.LocalDate

@TestMethodOrder(OrderAnnotation::class)
@Disabled
class NotionDairyTableTest {

    lateinit var db: DairyRepository

    private val token = "<secret>"
    private val notion = NotionClient(
        token,
        httpClient = OkHttp4Client(
            connectTimeoutMillis = 3 * 1000,
            readTimeoutMillis = 10 * 1000,
            writeTimeoutMillis = 10 * 1000
        )
    )
    private val path = NotionPath("/Junit Test/Junit Table")


    @BeforeEach
    fun create() {
        db = notion.get(path)
        db.clear()
    }

    @AfterEach
    fun remove() {
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
    fun get_first_last() {
        val month = LocalDate.now().withDayOfMonth(1)
        val first = DairyEntry(month.minusMonths(2), "Very good")
        val middle = DairyEntry(month.minusMonths(1), "Ok")
        val last = DairyEntry(month, "Not good")

        db.insert(last)
        db.insert(first)
        db.insert(middle)

        val entries = db.entries()
        assertEquals(3, entries.size)

        assertEquals(first, db.first().getOrNull())
        assertEquals(last, db.last().getOrNull())
        assertEquals(last, db.get(month).getOrNull())
        assertEquals(middle, db.get(month.minusMonths(1)).getOrNull())
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
        val month = LocalDate.now().withDayOfMonth(1)
        val first = DairyEntry(month.minusMonths(2), "Very good")
        val middle = DairyEntry(month.minusMonths(1), "Ok")
        val last = DairyEntry(month, "Not good")

        db.insert(last)
        db.insert(first)
        db.insert(middle)

        db.delete(month) // last
        val entries = db.entries()
        assertEquals(2, entries.size)

        assertEquals(middle, db.last().getOrNull())
    }
}