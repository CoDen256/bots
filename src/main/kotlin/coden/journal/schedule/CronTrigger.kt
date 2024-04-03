package coden.journal.schedule

import coden.journal.core.JournalInteractor
import coden.journal.core.request.Trigger
import dev.inmo.krontab.doInfinity
import kotlinx.coroutines.*

class CronTrigger(
    private val cron: String,
    dispatcher: CoroutineDispatcher,
    private val interactor: JournalInteractor,
): Trigger {

    private val scope: CoroutineScope = CoroutineScope(dispatcher)
    private lateinit var job: Job

    override fun start() {
        job = scope.launch {
            doInfinity(cron) {
                interactor.request()
            }
        }
    }

    override fun close() {
        job.cancel()
    }
}