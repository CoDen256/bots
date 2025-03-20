fun main() {
    val driver = createDriver()
    try {
        CLI(driver).run()
    } finally {
        driver.close()
        driver.quit()
    }
}

