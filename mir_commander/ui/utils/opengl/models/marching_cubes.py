import math

import numpy as np

EDGE_TABLE = [
    0x000,
    0x109,
    0x203,
    0x30A,
    0x406,
    0x50F,
    0x605,
    0x70C,
    0x80C,
    0x905,
    0xA0F,
    0xB06,
    0xC0A,
    0xD03,
    0xE09,
    0xF00,
    0x190,
    0x099,
    0x393,
    0x29A,
    0x596,
    0x49F,
    0x795,
    0x69C,
    0x99C,
    0x895,
    0xB9F,
    0xA96,
    0xD9A,
    0xC93,
    0xF99,
    0xE90,
    0x230,
    0x339,
    0x033,
    0x13A,
    0x636,
    0x73F,
    0x435,
    0x53C,
    0xA3C,
    0xB35,
    0x83F,
    0x936,
    0xE3A,
    0xF33,
    0xC39,
    0xD30,
    0x3A0,
    0x2A9,
    0x1A3,
    0x0AA,
    0x7A6,
    0x6AF,
    0x5A5,
    0x4AC,
    0xBAC,
    0xAA5,
    0x9AF,
    0x8A6,
    0xFAA,
    0xEA3,
    0xDA9,
    0xCA0,
    0x460,
    0x569,
    0x663,
    0x76A,
    0x066,
    0x16F,
    0x265,
    0x36C,
    0xC6C,
    0xD65,
    0xE6F,
    0xF66,
    0x86A,
    0x963,
    0xA69,
    0xB60,
    0x5F0,
    0x4F9,
    0x7F3,
    0x6FA,
    0x1F6,
    0x0FF,
    0x3F5,
    0x2FC,
    0xDFC,
    0xCF5,
    0xFFF,
    0xEF6,
    0x9FA,
    0x8F3,
    0xBF9,
    0xAF0,
    0x650,
    0x759,
    0x453,
    0x55A,
    0x256,
    0x35F,
    0x055,
    0x15C,
    0xE5C,
    0xF55,
    0xC5F,
    0xD56,
    0xA5A,
    0xB53,
    0x859,
    0x950,
    0x7C0,
    0x6C9,
    0x5C3,
    0x4CA,
    0x3C6,
    0x2CF,
    0x1C5,
    0x0CC,
    0xFCC,
    0xEC5,
    0xDCF,
    0xCC6,
    0xBCA,
    0xAC3,
    0x9C9,
    0x8C0,
    0x8C0,
    0x9C9,
    0xAC3,
    0xBCA,
    0xCC6,
    0xDCF,
    0xEC5,
    0xFCC,
    0x0CC,
    0x1C5,
    0x2CF,
    0x3C6,
    0x4CA,
    0x5C3,
    0x6C9,
    0x7C0,
    0x950,
    0x859,
    0xB53,
    0xA5A,
    0xD56,
    0xC5F,
    0xF55,
    0xE5C,
    0x15C,
    0x055,
    0x35F,
    0x256,
    0x55A,
    0x453,
    0x759,
    0x650,
    0xAF0,
    0xBF9,
    0x8F3,
    0x9FA,
    0xEF6,
    0xFFF,
    0xCF5,
    0xDFC,
    0x2FC,
    0x3F5,
    0x0FF,
    0x1F6,
    0x6FA,
    0x7F3,
    0x4F9,
    0x5F0,
    0xB60,
    0xA69,
    0x963,
    0x86A,
    0xF66,
    0xE6F,
    0xD65,
    0xC6C,
    0x36C,
    0x265,
    0x16F,
    0x066,
    0x76A,
    0x663,
    0x569,
    0x460,
    0xCA0,
    0xDA9,
    0xEA3,
    0xFAA,
    0x8A6,
    0x9AF,
    0xAA5,
    0xBAC,
    0x4AC,
    0x5A5,
    0x6AF,
    0x7A6,
    0x0AA,
    0x1A3,
    0x2A9,
    0x3A0,
    0xD30,
    0xC39,
    0xF33,
    0xE3A,
    0x936,
    0x83F,
    0xB35,
    0xA3C,
    0x53C,
    0x435,
    0x73F,
    0x636,
    0x13A,
    0x033,
    0x339,
    0x230,
    0xE90,
    0xF99,
    0xC93,
    0xD9A,
    0xA96,
    0xB9F,
    0x895,
    0x99C,
    0x69C,
    0x795,
    0x49F,
    0x596,
    0x29A,
    0x393,
    0x099,
    0x190,
    0xF00,
    0xE09,
    0xD03,
    0xC0A,
    0xB06,
    0xA0F,
    0x905,
    0x80C,
    0x70C,
    0x605,
    0x50F,
    0x406,
    0x30A,
    0x203,
    0x109,
    0x000,
]

TRIANGLE_TABLE = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1],
    [3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1],
    [3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1],
    [3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1],
    [9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
    [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1],
    [8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
    [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1],
    [3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1],
    [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1],
    [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1],
    [4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
    [5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1],
    [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1],
    [9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
    [0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
    [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1],
    [10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1],
    [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1],
    [5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1],
    [9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1],
    [1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1],
    [10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1],
    [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1],
    [2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1],
    [7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1],
    [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1],
    [11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1],
    [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1],
    [11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1],
    [11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1],
    [9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1],
    [2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1],
    [6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1],
    [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1],
    [6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
    [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1],
    [6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1],
    [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1],
    [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1],
    [3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1],
    [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1],
    [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1],
    [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1],
    [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1],
    [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1],
    [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1],
    [10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1],
    [10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1],
    [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1],
    [1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1],
    [0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1],
    [10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1],
    [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1],
    [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1],
    [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1],
    [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1],
    [3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1],
    [6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1],
    [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1],
    [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1],
    [10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1],
    [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1],
    [7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1],
    [7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1],
    [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1],
    [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1],
    [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1],
    [8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1],
    [0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1],
    [7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
    [10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
    [2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
    [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1],
    [7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1],
    [2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1],
    [10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1],
    [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1],
    [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1],
    [7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1],
    [6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1],
    [8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1],
    [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1],
    [6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1],
    [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1],
    [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1],
    [8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1],
    [0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1],
    [1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1],
    [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1],
    [10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1],
    [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1],
    [10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
    [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1],
    [9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
    [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1],
    [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1],
    [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1],
    [7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1],
    [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1],
    [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1],
    [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1],
    [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1],
    [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1],
    [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1],
    [6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1],
    [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1],
    [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1],
    [6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1],
    [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1],
    [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1],
    [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1],
    [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1],
    [9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1],
    [1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1],
    [1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1],
    [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1],
    [0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1],
    [5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1],
    [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1],
    [11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1],
    [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1],
    [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1],
    [2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1],
    [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1],
    [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1],
    [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1],
    [1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1],
    [9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1],
    [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1],
    [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1],
    [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1],
    [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1],
    [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1],
    [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1],
    [9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1],
    [5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1],
    [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1],
    [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1],
    [8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1],
    [0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1],
    [9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1],
    [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1],
    [3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1],
    [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1],
    [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1],
    [11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1],
    [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1],
    [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1],
    [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1],
    [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1],
    [1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1],
    [4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1],
    [3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1],
    [0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1],
    [1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
]


def _compute_gradient(
    scalar_field: np.ndarray, i: int, j: int, k: int, factor: float = 1.0
) -> tuple[float, float, float]:
    """
    Compute gradient at a given point using central differences.

    Args:
        scalar_field: The 3D scalar field
        i, j, k: Grid coordinates
        factor: Scale factor for field values

    Returns:
        Gradient vector (dx, dy, dz)
    """
    sx, sy, sz = scalar_field.shape

    # Central differences with boundary handling
    if i == 0:
        dx = factor * (scalar_field[i + 1, j, k] - scalar_field[i, j, k])
    elif i == sx - 1:
        dx = factor * (scalar_field[i, j, k] - scalar_field[i - 1, j, k])
    else:
        dx = factor * (scalar_field[i + 1, j, k] - scalar_field[i - 1, j, k]) * 0.5

    if j == 0:
        dy = factor * (scalar_field[i, j + 1, k] - scalar_field[i, j, k])
    elif j == sy - 1:
        dy = factor * (scalar_field[i, j, k] - scalar_field[i, j - 1, k])
    else:
        dy = factor * (scalar_field[i, j + 1, k] - scalar_field[i, j - 1, k]) * 0.5

    if k == 0:
        dz = factor * (scalar_field[i, j, k + 1] - scalar_field[i, j, k])
    elif k == sz - 1:
        dz = factor * (scalar_field[i, j, k] - scalar_field[i, j, k - 1])
    else:
        dz = factor * (scalar_field[i, j, k + 1] - scalar_field[i, j, k - 1]) * 0.5

    # Normalize gradient and invert (gradient points inward, we want outward normal)
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length > 1e-10:
        return (-dx / length, -dy / length, -dz / length)
    return (0.0, 0.0, -1.0)


def isosurface(scalar_field: np.ndarray, value: float, factor: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate triangles using Marching Cubes algorithm for isosurface extraction.

    Args:
        scalar_field: The 3D scalar field
        value: The isovalue for surface extraction
        factor: Scale factor for field values

    Returns:
        Tuple of (vertices, normals), both flattened as [x,y,z, x,y,z, ...]
    """
    vertices = []
    normals = []

    # Process each cube in the volume
    for i in range(scalar_field.shape[0] - 1):
        for j in range(scalar_field.shape[1] - 1):
            for k in range(scalar_field.shape[2] - 1):
                # Get the 8 corner values of the cube
                cube_values = [
                    factor * scalar_field[i][j][k],  # 0
                    factor * scalar_field[i + 1][j][k],  # 1
                    factor * scalar_field[i + 1][j + 1][k],  # 2
                    factor * scalar_field[i][j + 1][k],  # 3
                    factor * scalar_field[i][j][k + 1],  # 4
                    factor * scalar_field[i + 1][j][k + 1],  # 5
                    factor * scalar_field[i + 1][j + 1][k + 1],  # 6
                    factor * scalar_field[i][j + 1][k + 1],  # 7
                ]

                cube_positions = [
                    (i, j, k),  # 0
                    (i + 1, j, k),  # 1
                    (i + 1, j + 1, k),  # 2
                    (i, j + 1, k),  # 3
                    (i, j, k + 1),  # 4
                    (i + 1, j, k + 1),  # 5
                    (i + 1, j + 1, k + 1),  # 6
                    (i, j + 1, k + 1),  # 7
                ]

                # Compute gradients (normals) at each corner
                cube_normals = [
                    _compute_gradient(scalar_field, i, j, k, factor),  # 0
                    _compute_gradient(scalar_field, i + 1, j, k, factor),  # 1
                    _compute_gradient(scalar_field, i + 1, j + 1, k, factor),  # 2
                    _compute_gradient(scalar_field, i, j + 1, k, factor),  # 3
                    _compute_gradient(scalar_field, i, j, k + 1, factor),  # 4
                    _compute_gradient(scalar_field, i + 1, j, k + 1, factor),  # 5
                    _compute_gradient(scalar_field, i + 1, j + 1, k + 1, factor),  # 6
                    _compute_gradient(scalar_field, i, j + 1, k + 1, factor),  # 7
                ]

                # Calculate cube index based on which vertices are inside/outside
                cube_index = 0
                for vertex_idx in range(8):
                    if cube_values[vertex_idx] < value:
                        cube_index |= 1 << vertex_idx

                # Skip if cube is entirely inside or outside
                if EDGE_TABLE[cube_index] == 0:
                    continue

                # Find intersection points and normals on edges
                edge_vertices: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0)] * 12
                edge_normals: list[tuple[float, float, float]] = [(0.0, 0.0, 1.0)] * 12

                if EDGE_TABLE[cube_index] & 1:
                    edge_vertices[0] = _interpolate_vertex(
                        value, cube_positions[0], cube_positions[1], cube_values[0], cube_values[1]
                    )
                    edge_normals[0] = _interpolate_normal(
                        value, cube_normals[0], cube_normals[1], cube_values[0], cube_values[1]
                    )
                if EDGE_TABLE[cube_index] & 2:
                    edge_vertices[1] = _interpolate_vertex(
                        value, cube_positions[1], cube_positions[2], cube_values[1], cube_values[2]
                    )
                    edge_normals[1] = _interpolate_normal(
                        value, cube_normals[1], cube_normals[2], cube_values[1], cube_values[2]
                    )
                if EDGE_TABLE[cube_index] & 4:
                    edge_vertices[2] = _interpolate_vertex(
                        value, cube_positions[2], cube_positions[3], cube_values[2], cube_values[3]
                    )
                    edge_normals[2] = _interpolate_normal(
                        value, cube_normals[2], cube_normals[3], cube_values[2], cube_values[3]
                    )
                if EDGE_TABLE[cube_index] & 8:
                    edge_vertices[3] = _interpolate_vertex(
                        value, cube_positions[3], cube_positions[0], cube_values[3], cube_values[0]
                    )
                    edge_normals[3] = _interpolate_normal(
                        value, cube_normals[3], cube_normals[0], cube_values[3], cube_values[0]
                    )
                if EDGE_TABLE[cube_index] & 16:
                    edge_vertices[4] = _interpolate_vertex(
                        value, cube_positions[4], cube_positions[5], cube_values[4], cube_values[5]
                    )
                    edge_normals[4] = _interpolate_normal(
                        value, cube_normals[4], cube_normals[5], cube_values[4], cube_values[5]
                    )
                if EDGE_TABLE[cube_index] & 32:
                    edge_vertices[5] = _interpolate_vertex(
                        value, cube_positions[5], cube_positions[6], cube_values[5], cube_values[6]
                    )
                    edge_normals[5] = _interpolate_normal(
                        value, cube_normals[5], cube_normals[6], cube_values[5], cube_values[6]
                    )
                if EDGE_TABLE[cube_index] & 64:
                    edge_vertices[6] = _interpolate_vertex(
                        value, cube_positions[6], cube_positions[7], cube_values[6], cube_values[7]
                    )
                    edge_normals[6] = _interpolate_normal(
                        value, cube_normals[6], cube_normals[7], cube_values[6], cube_values[7]
                    )
                if EDGE_TABLE[cube_index] & 128:
                    edge_vertices[7] = _interpolate_vertex(
                        value, cube_positions[7], cube_positions[4], cube_values[7], cube_values[4]
                    )
                    edge_normals[7] = _interpolate_normal(
                        value, cube_normals[7], cube_normals[4], cube_values[7], cube_values[4]
                    )
                if EDGE_TABLE[cube_index] & 256:
                    edge_vertices[8] = _interpolate_vertex(
                        value, cube_positions[0], cube_positions[4], cube_values[0], cube_values[4]
                    )
                    edge_normals[8] = _interpolate_normal(
                        value, cube_normals[0], cube_normals[4], cube_values[0], cube_values[4]
                    )
                if EDGE_TABLE[cube_index] & 512:
                    edge_vertices[9] = _interpolate_vertex(
                        value, cube_positions[1], cube_positions[5], cube_values[1], cube_values[5]
                    )
                    edge_normals[9] = _interpolate_normal(
                        value, cube_normals[1], cube_normals[5], cube_values[1], cube_values[5]
                    )
                if EDGE_TABLE[cube_index] & 1024:
                    edge_vertices[10] = _interpolate_vertex(
                        value, cube_positions[2], cube_positions[6], cube_values[2], cube_values[6]
                    )
                    edge_normals[10] = _interpolate_normal(
                        value, cube_normals[2], cube_normals[6], cube_values[2], cube_values[6]
                    )
                if EDGE_TABLE[cube_index] & 2048:
                    edge_vertices[11] = _interpolate_vertex(
                        value, cube_positions[3], cube_positions[7], cube_values[3], cube_values[7]
                    )
                    edge_normals[11] = _interpolate_normal(
                        value, cube_normals[3], cube_normals[7], cube_values[3], cube_values[7]
                    )

                # Create triangles
                tri_idx = 0
                while TRIANGLE_TABLE[cube_index][tri_idx] != -1:
                    if value >= 0.0:
                        triangle = [
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][0],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][2],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][0],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][2],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][0],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][2],
                        ]
                        triangle_normals = [
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][2],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][2],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][2],
                        ]
                    else:
                        triangle = [
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][2],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx]][0],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][2],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 1]][0],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][2],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][1],
                            edge_vertices[TRIANGLE_TABLE[cube_index][tri_idx + 2]][0],
                        ]
                        triangle_normals = [
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx]][2],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 1]][2],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][0],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][1],
                            edge_normals[TRIANGLE_TABLE[cube_index][tri_idx + 2]][2],
                        ]
                    vertices.extend(triangle)
                    normals.extend(triangle_normals)
                    tri_idx += 3

    return (np.array(vertices, dtype=np.float32), np.array(normals, dtype=np.float32))


def _interpolate_vertex(
    isovalue: float, p1: tuple[float, float, float], p2: tuple[float, float, float], val1: float, val2: float
) -> tuple[float, float, float]:
    """Interpolate vertex position on edge based on isovalue."""
    if math.isclose(isovalue, val1, rel_tol=1e-6):
        return p1
    if math.isclose(isovalue, val2, rel_tol=1e-6):
        return p2
    if math.isclose(val1, val2, rel_tol=1e-6):
        return p1

    mu = (isovalue - val1) / (val2 - val1)
    return (
        p1[0] + (p2[0] - p1[0]) * mu,
        p1[1] + (p2[1] - p1[1]) * mu,
        p1[2] + (p2[2] - p1[2]) * mu,
    )


def _interpolate_normal(
    isovalue: float,
    n1: tuple[float, float, float],
    n2: tuple[float, float, float],
    val1: float,
    val2: float,
) -> tuple[float, float, float]:
    """Interpolate normal vector on edge based on isovalue."""
    if math.isclose(isovalue, val1, rel_tol=1e-6):
        return n1
    if math.isclose(isovalue, val2, rel_tol=1e-6):
        return n2
    if math.isclose(val1, val2, rel_tol=1e-6):
        return n1

    mu = (isovalue - val1) / (val2 - val1)
    nx = n1[0] + (n2[0] - n1[0]) * mu
    ny = n1[1] + (n2[1] - n1[1]) * mu
    nz = n1[2] + (n2[2] - n1[2]) * mu

    # Normalize interpolated normal
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length > 1e-10:
        return (nx / length, ny / length, nz / length)
    return (0.0, 0.0, 1.0)
