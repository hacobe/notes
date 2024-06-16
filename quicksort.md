# Quicksort

## Intuition

In merge sort, we divide the array in half and have to store each half. The key idea of Quicksort is that we can efficiently divide the array without creating additional arrays if in one pass of the array we can swap elements in such a way that one element moves to its final position in the sorted array and where all the elements to the left of that element are less than or equal to it and all the elements to the right are greater than it. Then, we can apply the same approach to the elements to the left and again to the elements to the right and so on until all the elements are in their final position in the sorted array.

## Stable Quicksort

Take a deck of cards. In merge sort, we split the deck in half, sorted each half and then merged the two sorted halves together and the way we sorted each half was to split the half in half, sort each quarter and then merge the quarters together and so on...

In Quicksort, we look at the first card in the deck and then scan through each card in the rest of the deck putting the cards less than (or equal to) the first card in one pile and the cards greater than the first card in another pile (an easier task than sorting the deck). Then we have a pile on the left, the first card, and a pile on the right. The first card is in its final position in the sorted deck, because all of the cards to the left it are less than or equal to it and all the cards to the right of it are greater than it. If we sorted the left pile and we sorted the right pile, then we would be done. But we can give the left pile to one friend to sort and the right pile to another friend to sort. Each friend can apply the same logic we have until a friend of friend ... of a friend has say 3 cards and they divide those 3 cards into a left pile, the first card and the right pile and they hand each pile to a friend to sort who just hands the 1 card in their pile back and says it is sorted, but then the 3 cards are sorted, because the left pile of 1 card is sorted and the right pile of 1 card is sorted and we know the card on the left is less than or equal to the first card and the card on the right is greater than the first card and this goes all the way back up until our left pile is sorted and our right pile is sorted and we know the entire deck is then sorted.

Instead of splitting the deck, sorting each half and then merging the sorted halves. In quick sort, we split the deck around the first card and sort each pile (not necessarily a half of the deck) on either side of the first card.

## Why Quicksort?

Why do this instead of merge sort? At this point, the analogy of the deck breaks down. In merge sort, splitting the deck in half requires additional memory, because it requires storing each half in its own array in addition to the input array (the deck). For quick sort, it turns that out we can divide the deck into 2 piles "in-place", i.e. by moving around elements in the input array rather than storing 2 new arrays (or by swapping cards while keeping the deck together rather than splitting the deck into piles).


Is there a way to do merge sort without storing the 2 halves? No. We can write a merge sort that sorts the left side of the array with one function call and the right side of the array with another function call without splitting the array. However, when we try to ”merge” the two sides of the array, we have a problem. Suppose we have an array `[4, 5, 6, 1, 2, 3]` where the left side is sorted and the right side is sorted. We compare the first element of the left side (4) and the first element of the right side (1) and find that the right side is smaller, but when we move the right side to the front of the array then we overwrite the first element on the left and can no longer compare that to the second element on the right side (2). We need to store at least half of the array.

## Unstable, in-place quicksort

Here’s an alternative way to divide the deck into 2 piles in quick sort without having to split the deck.

Place a white pawn on the second card in the deck and a black pawn on the last card in the deck.

Move the white pawn to right until we reach a card greater than the first card. Then, move the black pawn to the left until we reach a card less than the first card. Then, swap those 2 cards.

Continue this process of moving the white pawn to the right and the black pawn to the left and swapping cards until the white pawn crosses the black pawn or vice versa. At that point, we know that all of the cards to the left of the white pawn (including the card that the black pawn is on) are less than or equal to the first card, because the white pawn has passed through them and we would have swapped any card greater than the first card. Similarly, we know that all the cards to the right of the black pawn are greater than the first card. All we have to do now is to swap the first card with the black pawn card (which we know is less than or equal to the first card, because the white pawn has passed through it).

## Connection to Binary Search Trees

A certain flavor of quick sort is a space-optimized binary search tree sort. That flavor of quick sort requires:

* stable partition
* pivot is first element

In that flavor, each run of quick sort corresponds to a BST, where the root is the pivot and each left and right subtree is a side of the partition.

## Hoare vs Lomuto partitioning

We use the Hoare partitioning scheme below. Lomuto does not perform well for many repeated elements (https://www.geeksforgeeks.org/hoares-vs-lomuto-partition-scheme-quicksort/).

## Implementation

```python
import random

def _partition(nums, left, right):
    pivot = nums[left]
    l = left - 1
    r = right + 1
    while True:
        l += 1
        while nums[l] < pivot:
            l += 1
        
        r -= 1
        while nums[r] > pivot:
            r -= 1

        if l >= r:
            return r

        nums[l], nums[r] = nums[r], nums[l]

def _quicksort(nums, left, right):
    if left < right:
        pivot_index = _partition(nums, left, right)
        _quicksort(nums, left, pivot_index)
        _quicksort(nums, pivot_index+1, right)

def quicksort(nums):
    random.shuffle(nums)
    _quicksort(nums, 0, len(nums)-1)
    return nums
```
