from uni_block.contracts.base import BaseContract


class CourseContract(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "Course"


class StudentContract(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "Student"


class InstructorContract(BaseContract):
    _solidity_file = "solidity_code.sol"
    _contract_name = "Instructor"
