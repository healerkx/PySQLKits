
> 本人对数据设计的理解极其有限，但是依然不自量地想要通过一些自己臆断出来的原则来试图分析一个数据库的设计。

- 一个数据库设计，往往存在若干个主干表，主干表的主键往往是其他多个表的外键。那么主干表就是被依赖的表。
- 逻辑外键关系能表达一个表对另外一个表的依赖关系。

