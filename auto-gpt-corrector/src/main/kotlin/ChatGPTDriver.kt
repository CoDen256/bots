import org.openqa.selenium.By
import org.openqa.selenium.WebDriver
import org.openqa.selenium.WebElement

data class GPTDriverConfig(
    val delayOpenChat: Long,
    val delayEditButtonClick: Long
)

class ChatGPTDriver(
    private val driver: WebDriver,
    var config: GPTDriverConfig,
): WebDriver by driver, AutoCloseable  {
    private val regenerateButton = By.cssSelector("button.btn.relative.btn-primary.m-auto")
    private val promptTextArea = By.id("prompt-textarea")
    private val submitButton = By.cssSelector("button.absolute[data-testid]")

    private val stopGenerating = By.cssSelector("button[area-lable*=Stop]")

    private val saveAndSubmitEditButton = By.cssSelector("button.btn.btn-primary")
    private val editButton = By.cssSelector("div.self-end")
    private val editTextArea = By.cssSelector("textarea") // .filter { it.text.isNotBlank() }
    private val HOST = "https://chat.openai.com"
    private val DE_GPT = "/g/g-NyyZPpoWZ-de"


    private val messages = By.cssSelector("div.w-full.text-token-text-primary")
    fun openNewChat() {
        get(HOST)
        println("Open New Chat..., waiting ${config.delayOpenChat} ")
        delay(config.delayOpenChat)

    }

    fun openChat(id: String){
        get("$HOST/c/$id")
        println("Open Chat $id..., waiting ${config.delayOpenChat}")
        delay(config.delayOpenChat)
    }
    fun openDE(){
        get("$HOST$DE_GPT")
        println("Open DE GPT..., waiting ${config.delayOpenChat}")
        delay(config.delayOpenChat)
    }

    fun refresh(){
        navigate().refresh()
        println("Reloaded the window, waiting ${config.delayOpenChat}")
        delay(config.delayOpenChat)
    }

    fun tryRegenerate(){
        getElement(regenerateButton)?.let {
            it.click()
            println("Clicked regenerate button: $it, waiting ${config.delayOpenChat}")
            delay(config.delayOpenChat)
        }
    }

    fun isGenerating(): Boolean{
        return getElement(stopGenerating)?.isEnabled == true
    }

    fun tryGet(checkElement: () -> WebElement?): WebElement? {
        tryRegenerate()
        val promptArea = checkElement()
        if (promptArea != null) return promptArea
        println("Element not present, sorry.")
        refresh()

        return checkElement()
    }

    fun tryGetPromptArea(): WebElement? {
        return tryGet { getPromptText() }
    }

    fun getPromptText(): WebElement? {
        return getElement(promptTextArea)
    }


    fun getPromptSubmitButton(): WebElement? {
        return getElement(submitButton)
    }

    fun getMainArea(): Pair<WebElement?, WebElement?> {
        return getPromptText() to getPromptSubmitButton()
    }

    fun getEditText(): WebElement?{
        return findElements(editTextArea).firstOrNull { it.text.isNotBlank() }
    }

     fun getEditSubmitButton(): WebElement?{
        return findElements(saveAndSubmitEditButton).firstOrNull { it.text.isNotBlank() }
    }

    fun edit(message: Int): Pair<WebElement?, WebElement?>{
        val editButton = getEditButton(message)
        if (editButton?.isEnabled == false) {
            println("Not editable message $message")
            return null to null
        }
        editButton?.click()
        delay(config.delayEditButtonClick)
        return getEditArea()
    }

    fun getEditArea(): Pair<WebElement?, WebElement?> {
        return getEditText() to getEditSubmitButton()
    }

    fun getEditButton(message: Int): WebElement?{
        return findElements(messages)[message].findElements(editButton).lastOrNull()
    }

    fun isEditable(message: Int): Boolean{
        return getEditButton(message)?.isEnabled == true
    }

    fun getElement(selector: By): WebElement?{
        return findElements(selector).firstOrNull()
    }
}