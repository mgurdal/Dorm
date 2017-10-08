import models
import main

class Author(models.Model):
    """docstring for Author."""
    name = models.Char()

class Category(models.Model):
    """docstring for Category."""
    name = models.Char()

class Book(models.Model):
    """docstring for User."""
    name = models.Char()
    year = models.Integer()
    author = models.ForeignKey(Author)
    category = models.ManyToMany(Category)

if __name__ == '__main__':
    d = main.DORM()
