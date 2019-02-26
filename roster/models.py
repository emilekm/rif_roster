from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=255)
    squads = models.ManyToManyField('Squad', through='SquadRole')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Squad(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(Player, through='SquadRole')

    def __str__(self):
        return '{}. {}'.format(self.order, self.name)

    class Meta:
        ordering = ['order',]

class SquadRole(models.Model):
    CO = 0
    HCO = 1
    SL = 2
    NCO = 3
    GRUNT = 4
    RESERVE = 5
    ROLES = (
        (CO, 'Commander'),
        (HCO, 'Officer'),
        (SL, 'Squad Leader'),
        (NCO, 'NCO'),
        (GRUNT, 'Grunt'),
        (RESERVE, 'Reserve'),
    )
    role = models.IntegerField(choices=ROLES, default=RESERVE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {} of {}'.format(self.player, self.get_role_display(), self.squad)

    def get_ranked_player(self):
        return '{} - {}'.format(self.get_role_display(), self.player)

    def get_ranked_squad(self):
        return '{} - {}'.format(self.squad, self.get_role_display())

    class Meta:
        ordering = ['squad', 'role', 'player']
        unique_together = ('squad', 'player',)

