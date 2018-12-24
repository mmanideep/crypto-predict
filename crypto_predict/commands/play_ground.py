import datetime

from crypto_predict.commands.base import BaseCommand
from crypto_predict.models.bidding import UserBidModel, BetModel
from crypto_predict.periodic_tasks.update_bids_and_bets import FetchUpdateBids


class PlayGround(BaseCommand):

    def command(self, *args, **kwargs):
        for_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
        bet_models = BetModel.query.all()
        for bet in bet_models:
            bet.update(for_date=for_date)
        FetchUpdateBids().task()
        user_bids = UserBidModel.query.all()
        for user_bid in user_bids:
            print(user_bid.as_dict())
