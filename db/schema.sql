-- ===========================================================
-- SmartKitchen – Finales MySQL-Schema
-- Projekt: Verteilte Systeme  |  Stand: 2026-05-25
-- ===========================================================
-- Verwendung:
--   mysql -u root -p smart_kitchen < db/schema.sql
-- Oder über Alembic:
--   docker-compose exec backend alembic upgrade head
-- ===========================================================

SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------
-- 1. users
--    Speichert Benutzerdaten inkl. Argon2-Passworthash.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT       NOT NULL AUTO_INCREMENT,
    username      VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email    (email),
    INDEX ix_users_username (username),
    INDEX ix_users_email    (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 2. recipes
--    Kernentität – ein Rezept gehört genau einem User.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipes (
    id                 BIGINT       NOT NULL AUTO_INCREMENT,
    user_id            BIGINT,
    title              VARCHAR(255) NOT NULL,
    description        TEXT,
    prep_time_minutes  INT,
    servings           INT,
    difficulty         VARCHAR(50),   -- z. B. 'einfach', 'mittel', 'schwer'
    category           VARCHAR(100),
    is_public          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX ix_recipes_id (id),
    CONSTRAINT fk_recipes_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 3. recipe_ingredients
--    Strukturierte Zutatenliste für ein Rezept.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id         BIGINT       NOT NULL AUTO_INCREMENT,
    recipe_id  BIGINT,
    name       VARCHAR(255) NOT NULL,
    amount     FLOAT,
    unit       VARCHAR(50),
    PRIMARY KEY (id),
    CONSTRAINT fk_ingredients_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 4. recipe_steps
--    Schritt-für-Schritt-Anleitung zu einem Rezept.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_steps (
    id          BIGINT NOT NULL AUTO_INCREMENT,
    recipe_id   BIGINT,
    step_number INT,
    instruction TEXT  NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_steps_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 5. recipe_ratings
--    Bewertungen (1–5 Sterne) von Usern für Rezepte.
--    Ein User kann jedes Rezept genau einmal bewerten;
--    ein erneutes Bewerten überschreibt den Wert (PUT-Semantik).
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_ratings (
    id         BIGINT NOT NULL AUTO_INCREMENT,
    recipe_id  BIGINT,
    user_id    BIGINT,
    rating     INT    NOT NULL,   -- CHECK (rating BETWEEN 1 AND 5)
    PRIMARY KEY (id),
    CONSTRAINT fk_ratings_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ratings_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 6. tags
--    Globale Tag-Tabelle (normalisiert, kein Freitext pro Rezept).
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
    id    BIGINT       NOT NULL AUTO_INCREMENT,
    name  VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_tags_name (name),
    INDEX ix_tags_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 6b. recipe_tags  (M:N – Rezept ↔ Tag)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id  BIGINT NOT NULL,
    tag_id     BIGINT NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    CONSTRAINT fk_rt_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rt_tag
        FOREIGN KEY (tag_id) REFERENCES tags (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 7. groups
--    Benutzergruppen, die Rezepte teilen können.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS groups (
    id        BIGINT       NOT NULL AUTO_INCREMENT,
    name      VARCHAR(255) NOT NULL,
    owner_id  BIGINT,
    PRIMARY KEY (id),
    INDEX ix_groups_id (id),
    CONSTRAINT fk_groups_owner
        FOREIGN KEY (owner_id) REFERENCES users (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 7b. group_recipes  (M:N – Gruppe ↔ Rezept)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS group_recipes (
    group_id   BIGINT NOT NULL,
    recipe_id  BIGINT NOT NULL,
    PRIMARY KEY (group_id, recipe_id),
    CONSTRAINT fk_gr_group
        FOREIGN KEY (group_id) REFERENCES groups (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_gr_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
