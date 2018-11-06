
pragma solidity^0.4.17;

contract BaseUserAuth {

    address owner;

    bytes32 id;

    modifier onlyOwner {
        if (msg.sender != owner) {
            revert();
        }
        _;
    }

    constructor() public {
        owner=msg.sender;
    }

    function setId(bytes32 _id) ownerOnly public{
        id = _id;
    }

    function getId(bytes32 _id) ownerOnly public{
        return id;
    }

    function compareStrings (string a, string b) pure public returns (bool){
       return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b));
    }

    function getOwner() public returns (address){
        return owner;
    }

}

contract Course {

    string public course_code;

    uint credits;

    address instructor;

    address override;

    constructor() public{
        instructor = msg.sender;
        override = msg.sender;
    }

    modifier instructorOnly{
        if(msg.sender != instructor){
            revert();
        }
        _;
    }

    modifier overrideOnly{
        if(msg.sender != override){
            revert();
        }
        _;
    }

    function transfer_course_request(address new_instructor) instructorOnly() public {
        override = new_instructor;
        return true;
    }

    function accept_transfer_ownership() overrideOnly() public {
        instructor = override;
        return true;
    }

    function set_info(string _course_code, uint _credits) instructorOnly() public {
        course_code = _course_code;
        credits = _credits;
        return true;
    }

    function get_info() public view returns(address, uint, string, string){
        return (instructor, credits, course_code);
    }

    function grade_a_student(address _student, string grade) instructorOnly() public{
        Student stud = Student(_student);
        return stud.award_course(this, instructor, grade);
    }

}

contract Student is BaseUserAuth{

    struct course_info {
        string grade;
        address course_address;
        address instructor_account;
    }

    string [] total_courses;
    mapping(string => course_info) courses_map;

    uint total_credits = 0;

    function award_course(
            address course_contract_address, address _instructor_account, string grade
        )
        public returns (string, address, address)
    {

        require(msg.sender == _instructor_account, "Unauthorised access");

        course_info memory current_course;

        Course course = Course(course_contract_address);

        current_course.grade = grade;
        current_course.course_address = course_contract_address;
        current_course.instructor_account = course.instructor_account;

        total_credits += course.credits;

        total_courses.push(current_course.course_code);
        courses_map[current_course.course_code] = current_course;

        return (current_course.grade, current_course.course_address, current_course.instructor_account);

    }

    function can_award_degree() public view onlyOwner returns(bool) {

        if (total_credits > 50){
            return true;
        }
        return false;
    }

    function get_courses() public view returns (string[]){
        return total_courses;
    }

    function get_student_course_info(string _code) public view returns(string, address, address){
        return (courses_map[_code].grade, courses_map[_code].course_address, courses_map[_code].instructor_account);
    }

}


contract Instructor is BaseUserAuth{
    string[] courses;
    mapping(string => address) courses_map;

    function add_course(string code, uint credits) ownerOnly public {
        Course new_course = new Course();
        new_course.set_info(code, credits);
        courses.push(new_course.code);
        courses_map[new_course_code] = address(new_course);
    }

    function get_courses() public view returns(string[]){
        return (courses);
    }

    function get_course_info(string _course_code) public view returns(address){
        return courses_map[_course_code];
    }

}
