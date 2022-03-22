# test_idlist.py

from draftsman.blueprint import IDList

from unittest import TestCase


# class IDListTesting(TestCase):
#     def test_append(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")
#         self.assertEqual(
#             id_list,
#             [["item"], "string", {"set", "of", "strings"}]
#         )
#         self.assertEqual(
#             id_list.id_map,
#             {
#                 "string_id": "string",
#                 "wee": {"set", "of", "strings"}
#             }
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {
#                 1: "string_id",
#                 2: "wee"
#             }
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {
#                 "string_id": 1,
#                 "wee": 2
#             }
#         )

#     def test_clear(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")
#         id_list.clear()
#         self.assertEqual(id_list, [])
#         self.assertEqual(id_list.id_map, {})
#         self.assertEqual(id_list.num_to_key, {})
#         self.assertEqual(id_list.key_to_num, {})

#     # def test_copy(self):
#     #     pass

#     # def test_extend(self):
#     #     pass

#     # def test_index(self):
#     #     pass

#     # def test_insert(self):
#     #     pass

#     def test_pop(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")
#         # pop numeric index
#         id_list.pop(0)
#         self.assertEqual(
#             id_list,
#             ["string", {"set", "of", "strings"}]
#         )
#         self.assertEqual(
#             id_list.key_map,
#             {
#                 "string_id": "string",
#                 "wee": {"set", "of", "strings"}
#             }
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {0: "string_id", 1: "wee"}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {"string_id": 0, "wee": 1}
#         )
#         # pop string index
#         id_list.pop("wee")
#         self.assertEqual(
#             id_list,
#             ["string"]
#         )
#         self.assertEqual(
#             id_list.key_map,
#             {"string_id": "string"}
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {0: "string_id"}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {"string_id": 0}
#         )
#         id_list.pop(0)
#         self.assertEqual(
#             id_list,
#             []
#         )
#         self.assertEqual(
#             id_list.id_map,
#             {}
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {}
#         )

#     def test_remove(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")
#         id_list.remove("string")
#         self.assertEqual(
#             id_list,
#             [["item"], {"set", "of", "strings"}]
#         )
#         self.assertEqual(
#             id_list.id_map,
#             {"wee": {"set", "of", "strings"}}
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {1: "wee"}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {"wee": 1}
#         )
#         id_list.remove(["item"])
#         self.assertEqual(
#             id_list,
#             [{"set", "of", "strings"}]
#         )
#         self.assertEqual(
#             id_list.id_map,
#             {"wee": {"set", "of", "strings"}}
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {0: "wee"}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {"wee": 0}
#         )

#     # def test_reverse(self):
#     #     pass

#     # def test_sort(self):
#     #     pass

#     def test_getitem(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")
#         self.assertIs(id_list["string_id"], id_list[1])
#         self.assertIs(id_list["wee"], id_list[2])

#     def test_delitem(self):
#         id_list = IDList()
#         id_list.append(["item"])
#         id_list.append("string", "string_id")
#         id_list.append({"set", "of", "strings"}, "wee")

#         del id_list["string_id"]

#         self.assertEqual(
#             id_list,
#             [["item"], {"set", "of", "strings"}]
#         )
#         self.assertEqual(
#             id_list.id_map,
#             {"wee": {"set", "of", "strings"}}
#         )
#         self.assertEqual(
#             id_list.num_to_key,
#             {1: "wee"}
#         )
#         self.assertEqual(
#             id_list.key_to_num,
#             {"wee": 1}
#         )