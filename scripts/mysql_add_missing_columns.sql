-- Migration: add missing columns expected by app/mysql_data_layer.py
-- Requires MySQL 8+ for `IF NOT EXISTS` on ADD COLUMN / ADD INDEX

USE chainlit;

-- Thread table
ALTER TABLE `Thread`
  ADD COLUMN IF NOT EXISTS `userId` CHAR(36) NULL,
  ADD COLUMN IF NOT EXISTS `userIdentifier` VARCHAR(255) NULL;

-- Step table
ALTER TABLE `Step`
  ADD COLUMN IF NOT EXISTS `threadId` CHAR(36) NOT NULL,
  ADD COLUMN IF NOT EXISTS `parentId` CHAR(36) NULL,
  ADD COLUMN IF NOT EXISTS `startTime` DATETIME NULL,
  ADD COLUMN IF NOT EXISTS `endTime` DATETIME NULL,
  ADD COLUMN IF NOT EXISTS `isError` BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS `generation` JSON NULL,
  ADD COLUMN IF NOT EXISTS `feedback` JSON NULL;

ALTER TABLE `Step` ADD INDEX IF NOT EXISTS `idx_step_threadId` (`threadId`);

-- Element table
ALTER TABLE `Element`
  ADD COLUMN IF NOT EXISTS `threadId` CHAR(36) NULL,
  ADD COLUMN IF NOT EXISTS `forId` CHAR(36) NULL,
  ADD COLUMN IF NOT EXISTS `mime` VARCHAR(100) NULL,
  ADD COLUMN IF NOT EXISTS `metadata` JSON NULL;

ALTER TABLE `Element` ADD INDEX IF NOT EXISTS `idx_element_threadId` (`threadId`);

-- Feedback table
ALTER TABLE `Feedback`
  ADD COLUMN IF NOT EXISTS `stepId` CHAR(36) NOT NULL;

ALTER TABLE `Feedback` ADD INDEX IF NOT EXISTS `idx_feedback_stepId` (`stepId`);

-- User table (ensure columns exist)
ALTER TABLE `User`
  ADD COLUMN IF NOT EXISTS `identifier` VARCHAR(255) UNIQUE NOT NULL,
  ADD COLUMN IF NOT EXISTS `metadata` JSON NULL;

-- Notes:
-- If your MySQL version is older than 8.0 (no IF NOT EXISTS for ADD COLUMN),
-- please run the equivalent checks and ALTER statements manually or upgrade MySQL.
