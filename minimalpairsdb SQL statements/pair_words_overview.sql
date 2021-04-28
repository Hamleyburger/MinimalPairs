SELECT word, partner
FROM
(Select words.word, pairs.id as wid
FROM words
JOIN pairs ON pairs.word_id = words.id)
JOIN
(Select words.word as partner, pairs.id as pid
FROM words
JOIN pairs ON pairs.partner_id = words.id)
ON wid = pid;