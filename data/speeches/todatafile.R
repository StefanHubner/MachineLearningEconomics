install.packages("fuzzyjoin")
library(tidyverse)
library(fuzzyjoin)

meta <- read.table("./speeches.csv", sep = ";", header = TRUE) %>%
  mutate(Date = as.Date(Date, format = "%d %B %Y")) %>%
  arrange(Date) %>%

dftxt <- data.frame(matrix(nrow = nrow(meta)))
names(dftxt) <- "Speech"

for (i in 1:nrow(meta)) {
    date <- meta[i, ]$Date
    fn <- meta[i, ]$Filename
    lines <- readLines(paste0("./files/", fn))
    dftxt[i, "Speech"] <- str_replace_all(
                            paste(lines, collapse = " "),
                            "[[:punct:]]", "")
}

data <- cbind(meta, dftxt)

new_row <- tibble(Date = as.Date("2023-09-21"), Rate = 5.25, Decision = 0.0)

boe <- read.table("./boe.csv", sep = ",", header = TRUE) %>%
  mutate(Date = as.Date(Date.Changed, format = "%d %b %y")) %>%
  select(-Date.Changed) %>%
  arrange(Date) %>%
  mutate(Decision = c(0.0, diff(Rate))) %>%
  bind_rows(new_row)

result <- fuzzy_left_join(
  data,
  boe,
  by = c("Date" = "Date"),
  match_fun = list(`<=`)
) %>%
  group_by(Date.x) %>%
  filter(Date.y == min(Date.y[Date.y >= Date.x], na.rm = TRUE)) %>%
  ungroup() %>%
  select(Date = Date.x, Speech, Announcement = Date.y, Decision)

write.table(result, "speech_data.csv", sep = "♤", quote = FALSE)
