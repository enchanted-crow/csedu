class Decoder010:

    def __init__(self, query, ByteInput) -> None:
        self.ByteInput = ByteInput
        self.__ByteInput_list = ByteInput
        self.query_name = query[0]
        self.query_dest = query[1]
        self.query_type = query[2].upper()
        self.query_rr = (query[0], query[1], query[2])
        self.answer_rr = []
        self.authoritative_rr = []
        self.additional_rr = []
        self.q_type = None
        self.answer_count = 0
        self.authoritative_count = 0
        self.additional_count = 0
        self.__header_pos = []

    @staticmethod
    def __isHeader(list_12):
        if(list_12[2] == 0 and list_12[4] == 0 and list_12[6] == 0 and list_12[10] == 0):
            # print("OK")
            # print(list_12)
            return True
        # print("NOT OK")
        return False

    def __decode_answer(self, pos, final=False, q_type='A'):
        header_start = 0

        if(pos == 0):
            header_start = self.ans_start_pos()
            # print(header_start)
        else:
            header_start = self.__header_pos[pos][0]

        header_end = self.__header_pos[pos][1]

        rname = self.__ptr_extract_string(
            header_start, header_start + 2, True)

        if(final):
            rdata = ''
            rdata += str(self.__ByteInput_list[header_end + 1]) + '.'
            rdata += str(self.__ByteInput_list[header_end + 2]) + '.'
            rdata += str(self.__ByteInput_list[header_end + 3]) + '.'
            rdata += str(self.__ByteInput_list[header_end + 4])
            return rname, rdata

        rlength = self.__ByteInput_list[header_start + 11]

        if(q_type == 'MX'):
            rdata = self.__ptr_extract_string(
                header_end + 3, header_end + 3 + rlength - 2)
        elif(q_type == 'SOA'):
            rdata = self.__ptr_extract_string(
                header_end + 1, header_end + 1 + rlength, True)
        else:
            rdata = self.__ptr_extract_string(
                header_end + 1, header_end + 1 + rlength)

        return rname, rdata

    def ans_start_pos(self):
        return 12 + len(self.query_name) + 2 + 4

    def __ptr_extract_string(self, ptr_pos, last_pos, final=False):
        ret_str = ''
        i = ptr_pos
        while(i < last_pos):
            byte = self.__ByteInput_list[i]

            if(byte == 192):  # c0 - pointer
                ret_str += self.__ptr_extract_string(
                    self.__ByteInput_list[i + 1], last_pos, final)
                if(final):
                    return ret_str
                i += 2
            elif(byte == 0):
                return ret_str
            else:
                label_len = byte

                ret_str += '.'

                for j in range(i + 1, i + 1 + label_len):
                    ret_str += str(chr(self.__ByteInput_list[j]))

                i = i + 1 + label_len

        return ret_str

    @staticmethod
    def __get_qtype(header):
        qtype_int = header
        if(qtype_int == 1):
            return 'A'
        if(qtype_int == 2):
            return 'NS'
        if(qtype_int == 5):
            return 'CNAME'
        if(qtype_int == 6):
            return 'SOA'
        if(qtype_int == 15):
            return 'MX'

    def decode(self):
        ByteInput = self.ByteInput

        # 12 Byte buffer
        list_12 = []

        ByteInput_list = []

        # Extract first 12 Bytes
        i = 0
        for byte in ByteInput:
            list_12.append(byte)
            ByteInput_list.append(byte)
            if(i == 12 - 1):
                break
            i += 1

        # print(list_12)

        # 0 based, inclusive
        header_pos = []

        i = 0
        for byte in ByteInput:
            if(i < 12):
                i += 1
                continue

            # print(byte)

            list_12.pop(0)
            list_12.append(byte)
            ByteInput_list.append(byte)

            if(len(list_12) != 12):
                break

            if(Decoder010.__isHeader(list_12)):
                # print(str(i - (12 - 1)) + ' ' + str(i))
                header_pos.append((i - (12 - 1), i))

            i += 1
        self.__ByteInput_list = ByteInput_list
        self.__header_pos = header_pos

        # Answer part
        answer_count = int(ByteInput_list[7])
        authoritative_count = int(ByteInput_list[9])
        additional_count = int(ByteInput_list[11])

        if(answer_count):
            header_begin_pos = self.__header_pos[0][0]
            ans_type = Decoder010.__get_qtype(
                ByteInput_list[header_begin_pos + 3])

            decoded = None
            if(ans_type == 'A'):
                decoded = self.__decode_answer(0, q_type=ans_type, final=True)
                self.answer_rr = (decoded[0][1:], decoded[1], ans_type)
            elif(ans_type == 'MX' or ans_type == 'NS' or ans_type == 'CNAME'):
                decoded = self.__decode_answer(0, q_type=ans_type)
                self.answer_rr = (decoded[0][1:], decoded[1][1:], ans_type)
            # print('Answer: ' + self.answer_rr[1])
        if(authoritative_count):
            header_begin_pos = self.__header_pos[answer_count][0]
            ans_type = Decoder010.__get_qtype(
                ByteInput_list[header_begin_pos + 3])
            decoded = self.__decode_answer(answer_count, q_type=ans_type)
            self.authoritative_rr = (
                decoded[0][1:], decoded[1][1:], ans_type)
            # print('Auth: ' + self.authoritative_rr[0])
        if(additional_count):
            header_begin_pos = self.__header_pos[answer_count +
                                                 authoritative_count][0]
            ans_type = Decoder010.__get_qtype(
                ByteInput_list[header_begin_pos + 3])
            decoded = self.__decode_answer(
                answer_count + authoritative_count, q_type=ans_type, final=True)
            self.additional_rr = (decoded[0][1:], decoded[1], ans_type)
            # print('Additional: ' + self.additional_rr[0])

        self.answer_count = answer_count
        self.authoritative_count = authoritative_count
        self.additional_count = additional_count

        # print(self.answer_count)
        # print(self.authoritative_count)
        # print(self.additional_count)

        # print(self.answer_rr)
        # print(self.authoritative_rr)
        # print(self.additional_rr)

        # print()


if __name__ == '__main__':
    pass
    # main()
