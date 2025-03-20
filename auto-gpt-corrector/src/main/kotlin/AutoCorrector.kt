class AutoCorrector(
    driver: ChatGPTDriver,
    writer: TextAreaWriter,
) {


    fun writeSentences(vararg sentences: String) {
        writeSentences(sentences.toList())
    }

    fun writeSentences(sentences: List<String>) {
        sentences.withIndex().groupBy { it.index / 5 }
            .map { it.value }
            .forEach { l ->
                l.map { it.value }.forEach {
//                    writeAndSendAndWait(it, 50, 0, 50) }
//                onNewChat(this)
                }
            }
    }
}