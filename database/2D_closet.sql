DROP DATABASE IF EXISTS 2d_closet; -- to prevent ghost data
CREATE DATABASE 2d_closet; 
USE 2d_closet;

-- creating user's table
CREATE TABLE users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL
)ENGINE=InnoDB; -- engine: tells where to store data

-- items table with top, bottom dresses and outfits
CREATE TABLE items (
item_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
category ENUM('top', 'pant', 'skirt', 'dress') NOT NULL,
image_path VARCHAR(225) NOT NULL,
-- user_id as foreign key for items table
CONSTRAINT fk_items_user -- constraint name refering to a user for now
FOREIGN KEY  (user_id)
REFERENCES users(user_id) -- users = table
ON DELETE CASCADE -- AUTOMATic delete
) ENGINE = InnoDB;

-- OUTFITS TABLE
CREATE TABLE outfits(
outfit_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
top_id INT NULL,
bottom_id INT NULL,
dress_id INT NULL,
outfit_name VARCHAR(100),
	CONSTRAINT fk_outfits_user 
	FOREIGN KEY (user_id)
	REFERENCES users(user_id)
	ON DELETE CASCADE,
CONSTRAINT fk_outfit_top FOREIGN KEY (top_id) REFERENCES items(item_id) ON DELETE SET NULL,  -- items (table) item (id)
CONSTRAINT fk_outfit_bottom FOREIGN KEY (bottom_id) REFERENCES items(item_id) ON DELETE SET NULL,  -- top/bottom id not defined
CONSTRAINT fk_outfit_dress FOREIGN KEY (dress_id) REFERENCES items(item_id) ON DELETE SET NULL   -- they are foreign keys for outfits table
) ENGINE = InnoDB;

-- View all items in the user's closet
SELECT item_id, category, image_path 
FROM items 
WHERE user_id = 1;

-- "Swap" logic: User clicks a new pair of pants (ID: 10) for Outfit #1
UPDATE outfits 
SET bottom_id = 10 
WHERE outfit_id = 1 AND user_id = 1;

-- Delete a specific item
DELETE FROM items WHERE item_id = 5 AND user_id = 1;

-- show saved outfits with image pathhh
SELECT 
    o.outfit_name,
    i_top.image_path AS top_img,
    i_bottom.image_path AS bottom_img,
    i_dress.image_path AS dress_img
FROM outfits o
LEFT JOIN items i_top ON o.top_id = i_top.item_id  -- LEFT JOIN ensures outfits still appear even if an item is missing
LEFT JOIN items i_bottom ON o.bottom_id = i_bottom.item_id
LEFT JOIN items i_dress ON o.dress_id = i_dress.item_id
WHERE o.user_id = 1;


