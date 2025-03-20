import org.openqa.selenium.Keys
import org.openqa.selenium.WebDriver
import org.openqa.selenium.WebElement


data class WriterConfig(
    val delaySentence: Long,
    val delayMsPerCharRatio: Long,
    val delayChar: Long,
    val delayEnter: Long
)

class TextAreaWriter(driver: WebDriver,
                private val textArea: WebElement,
                private val submitButton: WebElement?,
                private val config: WriterConfig,
): WebDriver by driver {

    fun writeWithDelay(text: String) = apply {
        write(text)
        delay(text)
    }

    fun delay(sentence: String) = apply {
        val wait = config.delayMsPerCharRatio * sentence.length
        println("Delaying after sentence ${sentence.length} chars = $wait ms)")
        delay(wait)
    }

    fun selectLeftWord() = apply{
        textArea.sendKeys(Keys.LEFT_CONTROL, Keys.LEFT_SHIFT, Keys.ARROW_LEFT)
    }

    fun selectAll() = apply{
        textArea.sendKeys(Keys.LEFT_CONTROL, "a")
    }

    fun remove() = apply{
        textArea.sendKeys(Keys.BACK_SPACE)
    }

    fun removeLeftWord() = apply{
        selectLeftWord()
        remove()
    }

    fun removeAll() = apply{
        print("Removing everything in text field")
        selectAll()
        remove()
    }

    fun write(text: String) = apply {
        println("Writing text '${text.substring(0, text.length.coerceAtMost(10))}...'")
        val pureText = text.split("\n")

        for (line in pureText){
            if (config.delayChar == 0L){
                textArea.sendKeys(line)
                textArea.sendKeys(Keys.SHIFT, Keys.ENTER)
                continue
            }
            for (c in line) {
                textArea.sendKeys(c.toString())
                delay(config.delayChar)
            }
            textArea.sendKeys(Keys.SHIFT, Keys.ENTER)
        }

    }

    fun submit() = apply {
        println("Submitting in ${config.delayEnter}")
        delay(config.delayEnter)
        textArea.sendKeys(Keys.LEFT_CONTROL, Keys.ENTER)
    }

    fun pressSubmit() = apply {
        submitButton?.let {
            try {
                for (i in 0..10){
                    if (it.isEnabled){
                        it.click()
                        return@let
                    }
                    delay(1000)
                }
                print("Submit button is unavailable: $it")
                fallback()
            }catch (ex: Exception){
                delay(1000)
                fallback()
            }
        } ?: throw IllegalArgumentException("Should be a button to be clicked")
    }

    fun fallback(){
        println("Falling back")
        removeAll().write("Ja.")
    }
}