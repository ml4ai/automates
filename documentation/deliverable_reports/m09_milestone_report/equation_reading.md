## Equation Reading

Now that the team has a fully working implementation of the im2markup model, they have formatted and normalized data from one year of arxiv to use for training. This amounts to over 1.1M equation examples, an order of magnitude more training data than was used in the original and the newly gathered data represents a wide variety of domains (as compared to the original data which was only from particle physics). 
The team is currently training a model on this larger dataset.

Additionally, the team is working on data augmentation, as previously mentioned, and to complement that effort, they are beginning to implement the Spatial Transformer Network (STN; Jaderberg et al., 2015).  The STN is a differentiable module which learns to predict a spatial transformation for each image independently, in order to make the model as a whole invariant to any affine image tranformation, including translation, scaling, rotation, and shearing.  One advantage of the STN is that it is trained end-to-end with the rest of the model, not requiring direct supervision.  Instead it will learn to transform the image in such a way that the end task performance improves.


Jaderberg, M., Simonyan, K., & Zisserman, A. (2015). Spatial transformer networks. In Advances in neural information processing systems (pp. 2017-2025).
