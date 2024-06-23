from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Barbershopper(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Group(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(Barbershopper)

    def __str__(self):
        return self.name

class Quartet(Group):
    pass


class Chorus(Group):
    size = models.IntegerField()
    director = models.CharField(max_length=255)


class Judge(models.Model):
    person = models.ForeignKey(Barbershopper, on_delete=models.CASCADE)
    specialisation = models.CharField(max_length=255, choices=[("M", "Music"), ("P", "Performance"), ("S", "Singing"), ("A", "Admin")])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)



class Competition(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    judges = models.ManyToManyField(Judge)

    def __str__(self):
        return self.name

class Arrangement(models.Model):
    title = models.CharField(max_length=255)
    composer = models.ForeignKey(Barbershopper, on_delete=models.CASCADE, related_name="songs_composed")
    arranger = models.ForeignKey(Barbershopper, on_delete=models.CASCADE, related_name="songs_arranged")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def create_if_not_exists(cls, title, arranger):
        existing_arrangements = cls.objects.filter(title=title)
        if existing_arrangements.exists():
            return existing_arrangements.first()
        else:
            new_arrangement = cls(title=title, arranger=arranger, composer=arranger)
            new_arrangement.save()
            return new_arrangement

    def __str__(self):
        return self.title

class Scoresheet(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod 
    def import_

    def __str__(self):
        return f"{self.competition} - {self.created}"


class Result(models.Model):
    scoresheet = models.ForeignKey(Scoresheet, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    arrangement = models.ForeignKey(Arrangement, on_delete=models.CASCADE)
    music_score = models.DecimalField(max_digits=5, decimal_places=2)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2)
    singing_score = models.DecimalField(max_digits=5, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def total_score(self):
        return self.music_score + self.performance_score + self.singing_score

    @property
    def average_score(self):
        return self.total_score / 3

    def __str__(self):
        return f"{self.group} - {self.arrangement} - {self.scoresheet}"

