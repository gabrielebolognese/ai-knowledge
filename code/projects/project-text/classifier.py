"""The two sentiment classifiers: a bag of embeddings and a small bidirectional LSTM.

    python classifier.py      # parameter counts and a forward pass on a dummy batch
"""
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence


class BagOfEmbeddings(nn.Module):
    """Average the word vectors of a sentence, then one linear layer. Word order is ignored."""

    def __init__(self, vocab_size, emb_dim=64, num_classes=2, dropout=0.0):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=0)   # <pad> (id 0) stays a zero vector
        self.drop = nn.Dropout(dropout)
        self.out = nn.Linear(emb_dim, num_classes)

    def forward(self, ids, lengths):                   # ids: (batch, time), lengths: (batch,)
        vectors = self.emb(ids)                        # (batch, time, emb_dim)
        mask = (ids != 0).unsqueeze(-1).float()        # 1 for real words, 0 for padding
        mean = (vectors * mask).sum(1) / lengths.unsqueeze(1).float()   # average over real words only
        return self.out(self.drop(mean))               # (batch, num_classes) logits


class BiLSTMClassifier(nn.Module):
    """Read the sentence left-to-right and right-to-left; classify from both final hidden states."""

    def __init__(self, vocab_size, emb_dim=64, hidden=128, num_classes=2, dropout=0.3):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm = nn.LSTM(emb_dim, hidden, batch_first=True, bidirectional=True)
        self.drop = nn.Dropout(dropout)
        self.out = nn.Linear(2 * hidden, num_classes)

    def forward(self, ids, lengths):
        vectors = self.drop(self.emb(ids))
        packed = pack_padded_sequence(vectors, lengths.cpu(), batch_first=True, enforce_sorted=False)
        _, (h, _) = self.lstm(packed)                  # packing: padding never enters the LSTM
        both = torch.cat([h[-2], h[-1]], dim=1)        # forward direction's last state + backward's
        return self.out(self.drop(both))


MODELS = {"bag": BagOfEmbeddings, "bilstm": BiLSTMClassifier}


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())


def main():
    V = 14_712                                         # SST-2 training vocabulary (see sst2_data.py)
    ids = torch.tensor([[5, 9, 2, 0], [7, 3, 0, 0]])   # two sentences, padded to length 4
    lengths = torch.tensor([3, 2])
    for name, cls in MODELS.items():
        model = cls(V)
        emb = model.emb.weight.numel()
        print(f"{name:7s} {count_parameters(model):>9,} parameters "
              f"({emb:,} in the embedding table = {emb / count_parameters(model):.0%}); "
              f"output shape {tuple(model(ids, lengths).shape)}")


if __name__ == "__main__":
    main()
