-- Runs once, the first time the primary starts.
-- Creates the account the replica uses to copy data from the primary.
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replpass';
