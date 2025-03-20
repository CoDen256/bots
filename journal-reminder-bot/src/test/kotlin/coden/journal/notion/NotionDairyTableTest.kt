package coden.journal.notion

import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import coden.journal.notion.NotionDairyTableUtility.Companion.get
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
import java.time.YearMonth

@TestMethodOrder(OrderAnnotation::class)
@Disabled
class NotionDairyTableTest {

    lateinit var db: JournalRepository

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
        assertTrue(db.entries().getOrThrow().isEmpty())
    }

    @Test
    @Order(1)
    fun insert() {
        val month = YearMonth.now()
        val expected = JournalEntry(month, "Very good")
        db.insert(expected)
        val entries = db.entries()
        assertEquals(1, entries.getOrThrow().size)
        assertEquals(expected, entries.getOrThrow().first())
    }

    @Test
    fun get_first_last() {
        val month = YearMonth.now()
        val first = JournalEntry(month.minusMonths(2), "Very good")
        val middle = JournalEntry(month.minusMonths(1), "Ok")
        val last = JournalEntry(month, "Not good")

        db.insert(last)
        db.insert(first)
        db.insert(middle)

        val entries = db.entries()
        assertEquals(3, entries.getOrThrow().size)

        assertEquals(first, db.first().getOrNull())
        assertEquals(last, db.last().getOrNull())
        assertEquals(last, db.get(month).getOrNull())
        assertEquals(middle, db.get(month.minusMonths(1)).getOrNull())
    }


    @Test
    fun clear() {
        db.insert(JournalEntry(YearMonth.now(), "Alright"))
        db.insert(JournalEntry(YearMonth.now(), "Ok"))
        db.clear()
        assertTrue(db.entries().getOrThrow().isEmpty())
    }


    @Test
    fun delete() {
        val month = YearMonth.now()
        val first = JournalEntry(month.minusMonths(2), "Very good")
        val middle = JournalEntry(month.minusMonths(1), "Ok")
        val last = JournalEntry(month, "Not good")

        db.insert(last)
        db.insert(first)
        db.insert(middle)

        db.delete(month) // last
        val entries = db.entries()
        assertEquals(2, entries.getOrThrow().size)

        assertEquals(middle, db.last().getOrNull())
    }
}