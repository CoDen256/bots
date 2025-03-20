import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import java.io.File
import java.util.*

fun delay(delayMs: Long) {
    Thread.sleep(delayMs)
}

fun createOptions(): ChromeOptions {
    val options = ChromeOptions()
    options.addArguments("--user-data-dir=C:/Users/denbl/AppData/Local/Google/Chrome/User Data/")
    options.addArguments("--disable-extensions");
    options.setExperimentalOption("useAutomationExtension", false);
    options.setExperimentalOption("excludeSwitches", Collections.singletonList("enable-automation"))
    options.setExperimentalOption("detach", true)
    return options
}


fun createDriver(): ChromeDriver {
    killChromes()
    delay(1000)
    return ChromeDriver(createOptions())
}

fun killChromes() {
    Runtime.getRuntime().exec("taskkill /F /IM chrome.exe")
}


fun read(s: String): String {
    return File(s).readText()
}

fun purify(input: String): List<String> = input
    .replace("\r", "")
    .replace(":\n", ".")
    .replace("bzw.", "bzw")
    .replace("z.B.", "zum Beispiel")
    .replace("Z.B.", "Zum Beispiel")
    .replace("d.h.", "das heißt")
    .replace(Regex("\\[\\d+]"), "")
    .replace("\\d.*\\d", "1")
    .replace(Regex("-([a-z])"), "$1")
//    .replace(Regex("\\.\\s*([A-Z])"), "\n$1")
//    .replace(Regex("\\.\\s*$"), "\n")
    .replace(".", "\n")
    .split("\n")
    .asSequence()
    .filter { !it.matches(Regex("^\\d.*")) && it.split(" ").size > 4 }
    .filter { !it.matches(Regex("^Abbildung \\d .*")) }
    .filter { !it.matches(Regex("^Pipeline \\d .*")) }
    .filter { !it.matches(Regex("^Signalpattern \\d .*")) }
    .filter { !it.matches(Regex("^Listing \\d .*")) }
    .filter { it.isNotBlank() }
    .map { it.trim() }
    .map { "$it." }
    .toList()

fun main() {
    purify(read("input")).forEach { println(it) }
}