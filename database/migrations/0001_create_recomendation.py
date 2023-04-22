#
# file: migrations/0006_create_recomendation.py
#
from yoyo import step

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`recomendation`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `mood`.`recomendation` (
            `id_recomendation` INT NOT NULL,
            `content` VARCHAR(40) NULL,
            `recomendationcol` VARCHAR(4096) NULL,
            PRIMARY KEY (`id_recomendation`))
        ENGINE = InnoDB;
        """
    )
]
