from .fields import (_BaseFieldEnum, BidFields, PerExchangeBidFields,
                     AskFields, PerExchangeAskFields, BookFields)
import copy

class _BaseService:
    supports_subs = True
    supports_handlers = True
    implemented = True

    class Fields(_BaseFieldEnum):
        pass
        
    implemented = False

    @classmethod
    def normalize_fields(cls, msg):
        if 'content' in msg:
            new_msg = copy.deepcopy(msg)
            for component in new_msg['content']:
                cls.Fields.relabel_message(component)
            return new_msg
        return msg

class _BaseBookService(_BaseService):
    Fields = BookFields
    @classmethod
    def normalize_fields(cls, msg):
        # Relabel top-level fields
        new_msg = super().normalize_fields(msg)
        print(new_msg)
        # Relabel bids
        for content in new_msg['content']:
            if 'BIDS' in content:
                for bid in content['BIDS']:
                    # Relabel top-level bids
                    BidFields.relabel_message(bid)

                    # Relabel per-exchange bids
                    for e_bid in bid['BIDS']:
                        PerExchangeBidFields.relabel_message(e_bid)

        # Relabel asks
        for content in new_msg['content']:
            if 'ASKS' in content:
                for ask in content['ASKS']:
                    # Relabel top-level asks
                    AskFields.relabel_message(ask)

                    # Relabel per-exchange bids
                    for e_ask in ask['ASKS']:
                        PerExchangeAskFields.relabel_message(e_ask)
        print(msg, '\n', new_msg)
        return new_msg
