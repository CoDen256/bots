import org.openqa.selenium.WebDriver

class CLI(private val driver: WebDriver) {

    private val chatGPT: ChatGPTDriver = ChatGPTDriver(driver, GPTDriverConfig(3000, 2000))
    private lateinit var input: List<String>
    private lateinit var prompt: String

    private var writerConfig: WriterConfig = WriterConfig(1000, 0, 0, 1000)
    // n;i;p;psm;m Die Anforderungen sind erfullt;ise 2
    val commands: Map<String, (List<String>) -> Unit> = mapOf(
        "g" to { goto(it)},
        "n" to { newChat(it)},
        "i" to { inputRefresh(it)},
        "p" to { promptRefresh(it)},
        "c" to { gptCreate(it)},
        "w" to { writerConfigUpdate(it)},
        "d" to { newDE(it)},

        "e" to { writeSentenceInEdit(it)},
        "m" to { writeSentenceInMain(it)},

        "sm" to { writeSentencesInMain(it)},
        "se" to { writeSentencesInEdit(it)},

        "psm" to { writePromptInMain(it)},
        "ise" to { writeInputInEdit(it)},
        "ism" to { writeInputInMain(it)},
    )

    private fun newDE(it: List<String>) {
        chatGPT.openDE()
    }

    private fun writeInputInEdit(it: List<String>) {
        if (it.isEmpty()){
            println("can't write anything in edit:${it}")
            return
        }
        writeSentencesInEdit(listOf(it[0])+input)
    }

    private fun writeInputInMain(it: List<String>) {
        writeSentencesInMain(input)
    }

    private fun writePromptInMain(args: List<String>){
        writeSentenceInMain(listOf(prompt))
    }

    private fun writeSentencesInMain(args: List<String>){
        if (args.isEmpty()){
            println("WRONG NUMBER OF ARGS: ${args.size} but wanted > 0: $args")
            return
        }
        args.forEach {
            writeSentenceInMain(listOf(it))
            delay(1000)
        }

    }

    private fun writeSentencesInEdit(args: List<String>){
        if (args.isEmpty()){
            println("WRONG NUMBER OF ARGS: ${args.size} but wanted ${1}")
        }
        val message = args[0]
        args.drop(1).forEach {
            writeSentenceInEdit(listOf(message, it))
            delay(5000)
        }
    }

    private fun writeSentenceInMain(args: List<String>){
        if (args.size != 1){
            println("WRONG NUMBER OF ARGS: ${args.size} but wanted ${1}")
        }
        val (text, button) = chatGPT.getMainArea()
        if (text == null) {
            println("Text area is null, wtf to do idk")
        }

        val writer = TextAreaWriter(driver, text!!, button, writerConfig)
        writer
            .writeWithDelay(args[0])
            .submit()

        delay(10000)
    }

    private fun writeSentenceInEdit(args: List<String>){
        if (args.size != 2){
            println("WRONG NUMBER OF ARGS: ${args.size} but wanted ${2}: $args")
            return
        }

        val (text, button) = chatGPT.edit(args[0].toInt())
        if (text == null) {
            println("Text area is null, wtf to do idk")
            return
        }

        val writer = TextAreaWriter(driver, text, button, writerConfig)
        writer
            .removeAll()
            .writeWithDelay(args[1])
            .pressSubmit()
    }

    private fun writerConfigUpdate(args: List<String>) {
        println("Updating Writer Config $args")
        if (args.isEmpty() ){
            println("Nothing to update")
            return
        }
        if (args.size != 4){
            println("Args size not 4, but ${args.size}")
        }

        writerConfig = WriterConfig(
            args[0].toLong(),
            args[1].toLong(),
            args[2].toLong(),
            args[3].toLong(),
        )
    }

    private fun gptCreate(args: List<String>) {
        println("Updating GPT $args")
        if (args.isEmpty()){
            println("Nothing to update")
            return
        }
        if (args.size != 2){
            println("Args size not 2, but ${args.size}")
        }

        chatGPT.config = GPTDriverConfig(args[0].toLong(), args[0].toLong())
    }

    private fun promptRefresh(args: List<String>) {
        prompt = read("prompt")
        println("Read prompt: $prompt")
    }

    private fun inputRefresh(args: List<String>) {
        input = purify(read("input"))
        println("Read input: ${input}")
    }

    fun goto(args: List<String>) {
        if (args.isEmpty() ){
            println("Nothing to go to")
            return
        }
        val target = args[0]
        println("Going to $target")
        chatGPT.openChat(target)
    }


    fun newChat(args: List<String>) {
        println("Starting new chat")
        chatGPT.openNewChat()
    }

    fun run(){
        while (true){
            val input = readln()
            val cmds = input.split(";")
            println("Got commands: $cmds")
            for (cmd in cmds){
                if (!processCommand(cmd)) return
            }
        }
    }

    private fun processCommand(cmd: String): Boolean {
        println("Processing $cmd")
        val cmdAndArg = cmd.split(" ", limit = 2)
        val (fn, args) = cmdAndArg[0] to (cmdAndArg.getOrNull(1) ?: "").split("|")
        if (fn == "exit") return false
        commands[fn]?.invoke(args) ?: println("No command for $cmd")
        return true
    }
}