import itertools

import numpy as np
import torch
from torch.utils.data import Dataset


class IntegerSortDataset(Dataset):
	def __init__(self, num_samples=10000, low=0, high=100, min_len=1, max_len=10, seed=1):

		self.prng = np.random.RandomState(seed=seed)
		self.input_dim = high

		# Here, we assuming that the shape of each sample is a list of list of a single integer, e.g., [[10], [3], [5], [0]]
		# It is for an easier extension later even though it is not necessary for this simple sorting example
		self.seqs = [list(map(lambda x: [x], self.prng.choice(np.arange(low, high), size=self.prng.randint(min_len, max_len+1)).tolist())) for _ in range(num_samples)]
		self.labels = [sorted(range(len(seq)), key=seq.__getitem__) for seq in self.seqs]

	def __getitem__(self, index):
		seq = self.seqs[index]
		label = self.labels[index]

		len_seq = len(seq)
		row_col_index = list(zip(*[(i, number) for i, numbers in enumerate(seq) for number in numbers]))
		num_values = len(row_col_index[0])

		i = torch.LongTensor(row_col_index)
		v = torch.FloatTensor([1]*num_values)
		data = torch.sparse.FloatTensor(i, v, torch.Size([len_seq, self.input_dim]))

		return data, len_seq, label

	def __len__(self):
		return len(self.seqs)


def sparse_seq_collate_fn(batch):
	batch_size = len(batch)

	sorted_seqs, sorted_lengths, sorted_labels = zip(*sorted(batch, key=lambda x: x[1], reverse=True))

	padded_seqs = [seq.resize_as_(sorted_seqs[0]) for seq in sorted_seqs]

	# (Sparse) batch_size X max_seq_len X input_dim
	seq_tensor = torch.stack(padded_seqs)

	# batch_size
	length_tensor = torch.LongTensor(sorted_lengths)

	padded_labels = list(zip(*(itertools.zip_longest(*sorted_labels, fillvalue=-1))))

	# batch_size X max_seq_len (-1 padding)
	label_tensor = torch.LongTensor(padded_labels).view(batch_size, -1)

	# TODO: Currently, PyTorch DataLoader with num_workers >= 1 (multiprocessing) does not support Sparse Tensor
	# TODO: Meanwhile, use a dense tensor when num_workers >= 1.
	seq_tensor = seq_tensor.to_dense()

	return seq_tensor, length_tensor, label_tensor
