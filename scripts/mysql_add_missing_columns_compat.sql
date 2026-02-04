-- Migration compatible MySQL < 8.0
-- This script checks information_schema and executes ALTER statements
-- only when the target column/index doesn't already exist.

USE chainlit;

-- Helper: add column if missing
-- Usage pattern repeated for each column below

-- Thread.userId
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Thread' AND column_name = 'userId';
SET @stmt = 'ALTER TABLE `Thread` ADD COLUMN `userId` CHAR(36) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec;
PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Thread.userIdentifier
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Thread' AND column_name = 'userIdentifier';
SET @stmt = 'ALTER TABLE `Thread` ADD COLUMN `userIdentifier` VARCHAR(255) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec;
PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Step columns
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'threadId';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `threadId` CHAR(36) NOT NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'parentId';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `parentId` CHAR(36) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'startTime';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `startTime` DATETIME NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'endTime';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `endTime` DATETIME NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'isError';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `isError` BOOLEAN DEFAULT FALSE';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'generation';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `generation` JSON NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Step' AND column_name = 'feedback';
SET @stmt = 'ALTER TABLE `Step` ADD COLUMN `feedback` JSON NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Ensure index on Step.threadId
SELECT COUNT(*) INTO @idx_exists FROM information_schema.STATISTICS
 WHERE table_schema='chainlit' AND table_name='Step' AND index_name='idx_step_threadId';
SET @stmt = 'ALTER TABLE `Step` ADD INDEX `idx_step_threadId` (`threadId`)';
SELECT IF(@idx_exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Element columns
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Element' AND column_name = 'threadId';
SET @stmt = 'ALTER TABLE `Element` ADD COLUMN `threadId` CHAR(36) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Element' AND column_name = 'forId';
SET @stmt = 'ALTER TABLE `Element` ADD COLUMN `forId` CHAR(36) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Element' AND column_name = 'mime';
SET @stmt = 'ALTER TABLE `Element` ADD COLUMN `mime` VARCHAR(100) NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Element' AND column_name = 'metadata';
SET @stmt = 'ALTER TABLE `Element` ADD COLUMN `metadata` JSON NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Ensure index on Element.threadId
SELECT COUNT(*) INTO @idx_exists FROM information_schema.STATISTICS
 WHERE table_schema='chainlit' AND table_name='Element' AND index_name='idx_element_threadId';
SET @stmt = 'ALTER TABLE `Element` ADD INDEX `idx_element_threadId` (`threadId`)';
SELECT IF(@idx_exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Feedback.stepId
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'Feedback' AND column_name = 'stepId';
SET @stmt = 'ALTER TABLE `Feedback` ADD COLUMN `stepId` CHAR(36) NOT NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- Ensure index on Feedback.stepId
SELECT COUNT(*) INTO @idx_exists FROM information_schema.STATISTICS
 WHERE table_schema='chainlit' AND table_name='Feedback' AND index_name='idx_feedback_stepId';
SET @stmt = 'ALTER TABLE `Feedback` ADD INDEX `idx_feedback_stepId` (`stepId`)';
SELECT IF(@idx_exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- User table: ensure identifier and metadata exist (safe checks)
SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'User' AND column_name = 'identifier';
SET @stmt = 'ALTER TABLE `User` ADD COLUMN `identifier` VARCHAR(255) UNIQUE NOT NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

SELECT COUNT(*) INTO @exists FROM information_schema.COLUMNS
 WHERE table_schema = 'chainlit' AND table_name = 'User' AND column_name = 'metadata';
SET @stmt = 'ALTER TABLE `User` ADD COLUMN `metadata` JSON NULL';
SELECT IF(@exists=0,@stmt,'SELECT 1') INTO @toexec; PREPARE s FROM @toexec; EXECUTE s; DEALLOCATE PREPARE s;

-- End of migration
