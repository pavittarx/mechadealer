-- capital_remaining carried no information.
--
-- On users it was decremented in lockstep with capital on every allocation and
-- incremented in lockstep on every withdrawal, so the two were always equal.
-- On strategies the same was true: it moved only with capital, and nothing
-- ever decremented it when an order deployed capital.
--
-- Verified equal to capital in every row of both tables before dropping.
-- Free balance is now read from capital directly.

ALTER TABLE users DROP COLUMN IF EXISTS capital_remaining;
ALTER TABLE strategies DROP COLUMN IF EXISTS capital_remaining;
