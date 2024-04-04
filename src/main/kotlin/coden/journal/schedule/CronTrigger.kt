package coden.journal.schedule

import coden.journal.core.notify.Notifier
import coden.journal.core.Trigger
import dev.inmo.krontab.doInfinity
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import org.apache.logging.log4j.kotlin.Logging

class CronTrigger(
    private val cron: String,
    dispatcher: CoroutineDispatcher,
    private val notifier: Notifier,
): Trigger, Logging {

    private val scope: CoroutineScope = CoroutineScope(dispatcher)
    private lateinit var job: Job

    override fun start() {
        logger.info { "Launching trigger for $cron" }
        job = scope.launch {
            doInfinity(cron) {
                notifier.notify()
            }
        }
    }

    override fun close() {
        job.cancel()
    }
}