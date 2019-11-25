from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=255, unique=True)
    squads = models.ManyToManyField('Squad', through='SquadRole')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Squad(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=255)
    short = models.CharField(max_length=3)

    players = models.ManyToManyField(Player, through='SquadRole')

    def __str__(self):
        return '{}. {}'.format(self.order, self.name)

    class Meta:
        ordering = ['order',]

class SquadRole(models.Model):
    SCO = 0
    CO = 1
    XO = 2
    HCO = 3
    SL = 4
    NCO = 5
    GRUNT = 6
    RESERVE = 7
    ROLES = (
        (SCO, 'SCO'),
        (CO, 'CO'),
        (XO, 'XO'),
        (HCO, 'HCO'),
        (SL, 'SL'),
        (NCO, 'NCO'),
        (GRUNT, 'Grunt'),
        (RESERVE, 'Reserve'),
    )
    # ROLES = (
    #     (SCO, 'Supreme Commander'),
    #     (CO, 'Commander'),
        # (XO, 'Executive Commander'),
    #     (HCO, 'Officer'),
    #     (SL, 'Squad Leader'),
    #     (NCO, 'NCO'),
    #     (GRUNT, 'Grunt'),
    #     (RESERVE, 'Reserve'),
    # )
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

